from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = ROOT / ".github/workflows/deploy-demo.yml"
TEMPLATE_PATH = ROOT / "ops/azure-container-app.json"
DOCKERFILE_PATH = ROOT / "Dockerfile"


def test_container_frontend_build_includes_the_root_contract_registry() -> None:
    dockerfile = DOCKERFILE_PATH.read_text(encoding="utf-8")
    contract_copy = "COPY contracts/ ../contracts/"
    frontend_build = "RUN npm run build"
    assert contract_copy in dockerfile
    assert dockerfile.index(contract_copy) < dockerfile.index(frontend_build)


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
    assert container["resources"] == {"cpu": 2.0, "memory": "4Gi"}
    assert {item["name"]: item["value"] for item in container["env"]}[
        "LABELVERIFY_CLIENT_IDENTITY_SOURCE"
    ] == "azure_container_apps"
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
        probe["httpHeaders"] == [{"name": "Host", "value": "[parameters('allowedHost')]"}]
        for probe in probes.values()
    )
    assert all("tcpSocket" not in probe for probe in container["probes"])


def test_workflow_uses_oidc_digest_deployment_and_complete_smoke_gate(
    tmp_path: Path,
) -> None:
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
    assert "for attempt in 1 2 3; do" in workflow
    assert 'length == 3 and' in workflow
    assert '(.serverDurationMs | type) == "number"' in workflow
    assert ".serverDurationMs >= 0" in workflow
    assert '((map(.serverDurationMs) | add) / length) < 5000' in workflow
    assert '(map(.serverDurationMs) | max) < 9000' in workflow
    assert "durationsMs: map(.serverDurationMs)" in workflow
    assert "Full-sample server durations and statistics" in workflow
    assert "scripts/validate_product_corpus.py" in workflow
    assert "$global:LASTEXITCODE = 0" in root_gate
    assert "git grep -n -I -P" in root_gate
    assert "rg -n" not in root_gate
    assert ":(exclude)" not in root_gate
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
    readiness_step = "Prove container readiness before the Container App mutation boundary"
    mutation_step = "Mark the Container App mutation boundary"
    assert readiness_step in workflow
    assert workflow.index(readiness_step) < (
        workflow.index(mutation_step)
    )
    assert 'echo "ready=true" >>"$GITHUB_OUTPUT"' in workflow
    assert "PREDEPLOY_READY: ${{ steps.predeploy.outputs.ready }}" in workflow
    assert '[[ "$PREDEPLOY_READY" == "true" ]]' in workflow
    deployment_gate = (
        "${{ steps.predeploy.outputs.ready == 'true' &&\n"
        "              steps.mutation.outputs.started == 'true' }}"
    )
    deploy_start = workflow.index("Deploy the image digest through ARM")
    deploy_end = workflow.index("Validate the effective Azure configuration")
    assert deployment_gate in workflow[deploy_start:deploy_end]
    assert "docker logs \"$container_name\"" in workflow
    assert ".properties.configuration.ingress.fqdn == $host" in workflow
    assert ".properties.template.containers[0].resources.cpu == 2" in workflow
    assert '.properties.template.containers[0].resources.memory == "4Gi"' in workflow
    assert '.properties.configuration.identitySettings[0].lifecycle == "None"' in workflow
    assert ".identity.userAssignedIdentities | keys | map(ascii_downcase)" in workflow
    assert '.httpGet.path == "/health/ready"' in workflow
    assert "HTTP redirect" not in workflow or "redirect_status" in workflow

    uses = re.findall(r"^\s*uses:\s*([^\s#]+)", workflow, flags=re.MULTILINE)
    assert uses
    assert all(re.fullmatch(r"[^@]+@[0-9a-f]{40}", use) for use in uses)

    subprocess.run(["git", "init", "--quiet"], cwd=tmp_path, check=True, capture_output=True)
    research_path = tmp_path / "research" / "candidate.md"
    research_path.parent.mkdir()
    research_path.write_text(f"copied source {chr(0x2014)} blocked\n", encoding="utf-8")
    checksum_path = tmp_path / "release.sha256"
    checksum_path.write_text(f"snapshot {chr(0x2013)} blocked\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "research/candidate.md", "release.sha256"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    positive = subprocess.run(
        ["git", "grep", "-n", "-I", "-P", r"[\x{2010}-\x{2015}]", "--", "."],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert positive.returncode == 0
    assert "research/candidate.md" in positive.stdout
    assert "release.sha256" in positive.stdout


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
