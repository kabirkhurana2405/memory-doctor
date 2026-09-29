# Memory Doctor

**A local developer-diagnostics prototype for SDK/API contract checks, memory access diagnostics, and summary-grounding review.**

Memory Doctor is an independent Streamlit application built to explore developer experience around memory-enabled products. It brings several practical checks into one interface and exports reviewable JSON reports.

> **Project status:** Independent prototype. It is not an official TinyHumans or OpenHuman product. Hosted memory checks may be blocked for accounts without the required access.

## What it does

### SDK Contract Checker
- Loads an OpenAPI/Swagger JSON specification and lists documented operations.
- Inspects either the locally installed `tinyhumansai` Python package or uploaded Python source files.
- Uses static inspection to identify route patterns and compare them with the selected API contract.
- Refreshes the comparison when the specification or inspected source changes.
- Exports a JSON comparison report.

Static analysis does not execute SDK code. Dynamically constructed routes and routes hidden behind abstractions may not be detected. A route missing from a specification is not, by itself, proof that the live endpoint is unavailable.

### Memory Diagnostics
- Checks the public TinyHumans API health endpoint (`GET /health`) without a key.
- Performs a read-only access check against `GET /memory/events` with a user-supplied API key.
- Includes synthetic pipeline scenarios for demonstration: healthy pipeline, synced-but-not-searchable, embedding-worker failure, and retrieval failure.
- Exports JSON reports.

A successful health check only demonstrates that the health endpoint responded. It does not prove that memory ingestion or retrieval works. A `401` or `403` can reflect authentication, permissions, or hosted-product access restrictions; it should not automatically be interpreted as a memory-pipeline defect.

### Summary Grounding Lab
- Compares pasted source text with a generated summary using local, transparent heuristics.
- Flags summary expansion, candidate entities, dates and numbers not found in the source, and missing user-specified phrases.
- Shows descriptive charts for source/summary length and review candidates by check type.
- Exports a JSON report without including the original source or summary text.

The checks are heuristic review aids—not semantic entailment, hallucination detection, or a truth guarantee. A flagged item may be valid, and an absence of flags does not prove that a summary is grounded.

### Reports
- Keeps reports generated during the current Streamlit session.
- Allows reports to be downloaded again as JSON.
- Does not persist report history across sessions.

## Interface

Screenshots below are captured from the running application. See the [screenshot guide](docs/SCREENSHOTS.md) for the file list and capture notes.

### Dashboard

![Memory Doctor dashboard](docs/images/dashboard.png)

### SDK Contract Checker

![SDK Contract Checker — view 1](docs/images/sdk-checker-1.png)

![SDK Contract Checker — view 2](docs/images/sdk-checker-2.png)

### Memory Diagnostics

![Memory Diagnostics — view 1](docs/images/memory-diagnostics-1.png)

![Memory Diagnostics — view 2](docs/images/memory-diagnostics-2.png)

### Summary Grounding Lab

![Summary Grounding Lab — view 1](docs/images/grounding-lab-1.png)

![Summary Grounding Lab — view 2](docs/images/grounding-lab-2.png)

## Quick start

### Requirements
- Python 3.10 or later
- pip
- Git (optional, for version control)
- `tinyhumansai` is optional and is only needed for the installed-package inspection mode.

### Windows (PowerShell)

From the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the application:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

To inspect an installed TinyHumans SDK package, install it into the same virtual environment used to run Streamlit:

```powershell
.\.venv\Scripts\python.exe -m pip install tinyhumansai
```

Alternatively, use the SDK source-upload mode in the app. Uploaded code is parsed statically and is not executed.

### macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

## Tests

Run the test suite from the repository root.

Windows:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

macOS / Linux:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

The current tests cover the route/contract checker and the summary-grounding heuristics. Live API availability and hosted-memory authorization are environment- and account-dependent; the unit tests do not validate those external services.

## Project structure

```text
memory-doctor/
├── app.py
├── memory_doctor/
│   └── core/
│       ├── api_client.py
│       ├── contract_checker.py
│       └── grounding_checker.py
├── tests/
│   ├── test_contract_checker.py
│   └── test_grounding_checker.py
├── .streamlit/
│   └── config.toml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── LIMITATIONS.md
│   ├── SCREENSHOTS.md
│   ├── SECURITY.md
│   ├── USER_GUIDE.md
│   └── images/
│       ├── dashboard.png
│       ├── sdk-checker-1.png
│       ├── sdk-checker-2.png
│       ├── memory-diagnostics-1.png
│       ├── memory-diagnostics-2.png
│       ├── grounding-lab-1.png
│       └── grounding-lab-2.png
├── requirements.txt
└── README.md
```

## Security and privacy

- Do not commit API keys, `.env` files, session tokens, customer data, or private memory exports.
- The memory-access field is masked in the UI. Treat the key as sensitive and do not share screenshots that reveal it.
- JSON reports omit API credentials; grounding reports omit source and summary text.
- Use synthetic or sanitized material for screenshots and examples.
- See [Security notes](docs/SECURITY.md).

## Documentation

- [User guide](docs/USER_GUIDE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Limitations and interpretation](docs/LIMITATIONS.md)
- [Security notes](docs/SECURITY.md)
- [Screenshot guide](docs/SCREENSHOTS.md)

## Background

This prototype grew out of hands-on testing of a Python SDK and the developer workflow around a memory API. It is intended to make integration evidence easier to inspect and communicate—not to assert that every observed failure is a product defect. The accompanying findings distinguish reproducible SDK/documentation discrepancies from account-access questions and unverified hosted behavior.

## License

No license has been specified yet. Until a license is added, assume that standard copyright restrictions apply to reuse of this repository.
