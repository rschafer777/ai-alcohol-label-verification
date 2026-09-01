from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = ROOT / ".github/workflows/deploy-demo.yml"
TEMPLATE_PATH = ROOT / "ops/azure-container-app.json"


def test_deployment_template_has_the_governed_runtime_shape() -> None:
    template = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    assert template["resources"] and len(template["resources"]) == 1
    app = template["resources"][0]
    assert app["type"] == "Microsoft.App/containerApps"
    assert app["apiVersion"] == "2026-01-01"
    assert app["identity"]["type"] == "UserAssigned"

    properties = app["properties"]
    assert properties["workloadProfileName"] == "Consumption"
    configuration = properties["configuration"]
    assert configuration["activeRevisionsMode"] == "Single"
    assert configuration["secrets"] == []
    assert configuration["ingress"] == {
        "external": True,
        "allowInsecure": False,
        "targetPort": 8080,
        "transport": "auto",
    }
    assert len(configuration["registries"]) == 1
    assert configuration["registries"][0]["identity"] == "[parameters('pullIdentityResourceId')]"

    runtime = properties["template"]
    assert runtime["volumes"] == []
    assert runtime["terminationGracePeriodSeconds"] == 30
    assert runtime["scale"]["minReplicas"] == 0
    assert runtime["scale"]["maxReplicas"] == 1
    assert runtime["scale"]["rules"][0]["http"]["metadata"]["concurrentRequests"] == "1"
    assert len(runtime["containers"]) == 1
    container = runtime["containers"][0]
    assert container["name"] == "labelverify"
    assert container["resources"] == {"cpu": 1.0, "memory": "2Gi"}
    assert {probe["type"] for probe in container["probes"]} == {
        "Startup",
        "Liveness",
        "Readiness",
    }
    assert all(probe["tcpSocket"] == {"port": 8080} for probe in container["probes"])
    assert all("httpGet" not in probe for probe in container["probes"])


def test_workflow_uses_oidc_digest_deployment_and_complete_smoke_gate() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "environment:\n      name: demo" in workflow
    assert "id-token: write" in workflow
    assert "azure/login@" in workflow
    assert "client-id: ${{ secrets.AZURE_CLIENT_ID }}" in workflow
    assert "tenant-id: ${{ secrets.AZURE_TENANT_ID }}" in workflow
    assert "subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}" in workflow
    assert "az acr login" in workflow
    assert "@${IMAGE_DIGEST}" in workflow
    assert "ops/azure-container-app.json" in workflow
    assert "/health/ready" in workflow
    assert "/api/v1/meta" in workflow
    assert "/api/v1/verifications" in workflow
    assert "Origin: $base_url" in workflow
    assert "selectedCheckCount == 19" in workflow
    assert "HTTP redirect" not in workflow or "redirect_status" in workflow

    uses = re.findall(r"^\s*uses:\s*([^\s#]+)", workflow, flags=re.MULTILINE)
    assert uses
    assert all(re.fullmatch(r"[^@]+@[0-9a-f]{40}", use) for use in uses)


def test_public_source_contains_no_effective_azure_identifiers() -> None:
    public_contract = "\n".join(
        [
            WORKFLOW_PATH.read_text(encoding="utf-8"),
            TEMPLATE_PATH.read_text(encoding="utf-8"),
        ]
    )
    assert re.search(r"\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b", public_contract) is None
    assert "/subscriptions/" not in public_contract.casefold()
    assert "azurewebsites.net" not in public_contract.casefold()
