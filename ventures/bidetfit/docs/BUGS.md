# BidetFit Bug Ledger

## BF-009 — Python standard-library shadowing prevented operator startup

**Status:** Done  
**Severity:** P0  
**Detected:** 2026-08-25  
**Impact:** The new unattended operator failed before reading state or running health checks.  
**Root cause:** Executing `ventures/bidetfit/scripts/operator.py` by file path placed that directory first on Python’s import path. The local `operator.py` then shadowed Python’s standard-library `operator` module while `enum` was importing.  
**Repair:** Invoke the script as a module: `python3 -m ventures.bidetfit.scripts.operator`. Preserve failure evidence and always commit available run state.  
**Verification:** External run `32868199605` completed successfully, fetched the public status endpoint with HTTP 200, and committed state and run evidence.  
**Regression prevention:** The workflow uses module execution; future CI must keep a direct operator smoke test.

## BF-010 — Deployment appeared failed after a healthy public release

**Status:** Done  
**Severity:** P1  
**Detected:** 2026-08-25  
**Impact:** The workflow’s overall badge was red even though build, Pages deployment, and public BidetFit verification had passed.  
**Root cause:** The incident-cleanup `gh issue` command executed without repository context after the verification job and failed outside a checked-out repository.  
**Repair:** Supply explicit repository context to the issue command.  
**Verification:** Overlay run `32868820325` completed build, deploy, verify, and incident cleanup successfully.  
**Lesson:** Diagnose workflow status at the step level and keep artifact health separate from reporting and cleanup health.

## Open bug policy

Every new production defect receives a stable BF work-item ID, severity, reproducible current state, impact, root-cause evidence, repair scope, regression test, deployment evidence, and documentation/Jira/Notion synchronization before Done.
