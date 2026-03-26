# SOLIDGOAT

# SOLID Framework Prototype

This project is a Python-based prototype for detecting and mock-refactoring SOLID design principle violations in a repository.

It was built as an initial framework for the course workflow:
- scan a repository
- detect potential SOLID violations
- store findings in a registry with deduplication
- apply mock refactors automatically
- run tests automatically
- save run artifacts for later review

## Current Scope

The current prototype supports:
- `SRP`, `OCP`, `LSP`, `ISP`, and `DIP` detector passes
- repository scanning for Python files
- structured issue records with:
  - `principle`
  - `file`
  - `class`
  - `method`
  - `symbol_name`
  - `line_range`
  - `reasoning`
  - `confidence`
- issue deduplication
- baseline and post-refactor test execution
- artifact output:
  - per-principle detections
  - scan summary
  - review queue
  - refactor attempts
  - PR-style report

The current implementation is still a prototype:
- the LLM layer is mocked
- refactoring is a mock code update
- detectors are heuristic-based and can produce many false positives

## Expected Project Layout

The framework was implemented around this structure:

```text
solid_framework/
├── main.py
├── config.py
├── core/
│   ├── detector.py
│   ├── llm.py
│   ├── refactor.py
│   └── registry.py
├── runners/
│   └── test_runner.py
├── utils/
│   ├── artifacts.py
│   ├── file_loader.py
│   └── logger.py
├── tests/
│   ├── test_pipeline_smoke.py
│   └── test_runner_target.py
└── data/
    ├── issues.json
    └── runs/
```

## How To Run

### 1. Run the framework on itself

If the framework source files are present in this directory, run:

```bash
python3 main.py /Users/elsteel/solid_framework --test-target tests/test_runner_target.py
```

This performs:
- baseline tests
- one scan per SOLID principle
- up to 2 mock refactor attempts by default
- artifact generation under `data/runs/`

### 2. Run a single-principle scan

```bash
python3 main.py /path/to/repo --principle SRP
```

Valid values:
- `SRP`
- `OCP`
- `LSP`
- `ISP`
- `DIP`

### 3. Restrict analysis scope

To scan only a specific subdirectory:

```bash
python3 main.py /path/to/repo --scan-root xarray
```

You can repeat `--scan-root` if needed.

### 4. Control refactor count

```bash
python3 main.py /path/to/repo --max-refactors 2
```

### 5. Pass explicit pytest targets

```bash
python3 main.py /path/to/repo --test-target /absolute/path/to/test_file.py
```

This is useful when the full repo test suite is too large or requires unavailable dependencies.

## Running the xarray Trial

Assigned repository:
- `pydata/xarray`

Local clone used for the initial trial:
- `/Users/elsteel/xarray`

### Environment setup used

```bash
python3 -m venv /Users/elsteel/xarray/.venv
/Users/elsteel/xarray/.venv/bin/python -m pip install numpy pandas pytest
```

### Command used for the real trial run

```bash
/Users/elsteel/xarray/.venv/bin/python /Users/elsteel/solid_framework/main.py /Users/elsteel/xarray --scan-root xarray --test-target /Users/elsteel/xarray/xarray/tests/test_assertions.py
```

This run:
- scanned `xarray/`
- performed 1 scan for each SOLID principle
- recorded detections
- ran baseline tests
- executed 2 mock refactor attempts
- reran tests after refactoring
- generated review and report artifacts

## Trial Artifacts

Artifacts from the `xarray` trial are stored in:

```text
/Users/elsteel/solid_framework/data/runs/20260326_174916_xarray
```

Important files:
- `scan_summary.json`
- `detections_SRP.json`
- `detections_OCP.json`
- `detections_LSP.json`
- `detections_ISP.json`
- `detections_DIP.json`
- `manual_review_queue.json`
- `manual_review_completed.json`
- `refactor_attempts.json`
- `pr_report.md`

## What To Do Next

For the next stage of the project, the most important improvements are:
- reduce detector false positives
- avoid flagging abstract/interface-only methods as violations
- replace mock LLM outputs with real API calls
- replace mock refactor comments with real structured patches
- add before/after code quality metrics
- add proper manual annotation workflow
- add precision, recall, and F1 computation
- add attempt-budget tracking for the course requirements

## Important Note

The real `xarray` trial modified this file with mock refactor comments:

```text
/Users/elsteel/xarray/xarray/backends/common.py
```

If you want a clean repo state before the next experiment, restore or reclone the repository before running additional trials.
