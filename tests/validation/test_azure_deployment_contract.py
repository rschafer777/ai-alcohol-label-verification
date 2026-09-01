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
    assert configuration["identitySettings"] == [
        {
            "identity": "[parameters('pullIdentityResourceId')]",
            "lifecycle": "None",
        }
    ]

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
    assert {
        item["name"]: item["value"] for item in container["env"]
    }["LABELVERIFY_CLIENT_IDENTITY_SOURCE"] == "azure_container_apps"
    assert {probe["type"] for probe in container["probes"]} == {
        "Startup",
        "Liveness",
        "Readiness",
    }
    probes = {probe["type"]: probe["httpGet"] for probe in container["probes"]}
    assert probes["Startup"]["path"] == "/health/live"
    assert probes["Liveness"]["path"] == "/health/live"
    assert probes["Readiness"]["path"] == "/health/ready"
    assert all(probe["port"] == 8080 for probe in probes.values())
    assert all(probe["scheme"] == "HTTP" for probe in probes.values())
    assert all(
        probe["httpHeaders"]
        == [{"name": "Host", "value": "[parameters('allowedHost')]"}]
        for probe in probes.values()
    )
    assert all("tcpSocket" not in probe for probe in container["probes"])


def test_workflow_uses_oidc_digest_deployment_and_complete_smoke_gate() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    root_gate = (ROOT / "scripts/check.ps1").read_text(encoding="utf-8")
    assert re.search(r"^  push:", workflow, flags=re.MULTILINE) is None
    assert "workflow_dispatch:" in workflow
    assert "if: github.ref == 'refs/heads/main'" in workflow
    assert "astral-sh/setup-uv" not in workflow
    assert 'python -m pip install --disable-pip-version-check "uv==0.11.32"' in workflow
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
    assert '.summary == "Review needed"' in workflow
    assert "scripts/validate_product_corpus.py" in workflow
    assert "$global:LASTEXITCODE = 0" in root_gate
    assert "scripts/scan_public_personal_details.py" in workflow
    assert "secrets.LABELVERIFY_PROHIBITED_PERSONAL_TERMS" in workflow
    assert workflow.index("Capture a governed prior deployment") < workflow.index(
        "Build and push the immutable image"
    )
    assert "${{ vars.AZURE_IMAGE_NAME }}:demo" not in workflow
    assert "The prior image is not a governed immutable digest." in workflow
    assert "needs.deploy.outputs.prior_image" in workflow
    assert "needs.deploy.outputs.prior_deployment" in workflow
    assert "az deployment group export" in workflow
    assert "labelverify-rollback-" in workflow
    assert "The prior digest was restored and verified." in workflow
    assert "The new Container App was removed." in workflow
    assert '.properties.configuration.ingress.fqdn == $host' in workflow
    assert '.properties.configuration.identitySettings[0].lifecycle == "None"' in workflow
    assert ".identity.userAssignedIdentities | keys | map(ascii_downcase)" in workflow
    assert '.httpGet.path == "/health/ready"' in workflow
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
