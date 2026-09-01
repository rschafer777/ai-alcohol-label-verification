# Development Toolchain Baseline

Document control ID: LV-DEV-002  
Revision: 1.0  
Date: 2026-09-01  
Status: Active

## Host tools

| Tool | Observed version | Status |
|---|---|---|
| Python | 3.12.10 | Available |
| uv | 0.11.32 | Available |
| Node.js | 24.14.0 | Available |
| npm | 11.9.0 | Available |
| Docker | Not installed | Local OCI assertions remain BLOCKED until a builder is available |

## Locked environments

- Python dependency resolution is recorded in `uv.lock`.
- Frontend dependency resolution is recorded in `frontend/package-lock.json`.
- `uv sync` completed successfully with 55 installed packages.
- `npm install` completed successfully with 0 reported vulnerabilities.
- jsdom is pinned to 29.1.1 because jsdom 30 requires Node 24.15.0 or newer and this host has Node 24.14.0.
- TypeScript is pinned to 6.0.3 because the selected `typescript-eslint` line requires TypeScript below 6.1.

## Current gate effect

Local source development, unit tests, integration tests, and browser build/test work are available. The four mandatory local OCI assertions cannot pass on this host until a compatible container builder is provided. BI requires BLOCKED/INCOMPLETE status rather than a false PASS while that prerequisite is absent.
