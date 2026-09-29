# Architecture

## Overview

Memory Doctor is a small Streamlit application with a thin UI layer and three core Python modules.

```text
Browser
  │
  ▼
Streamlit app.py
  ├── SDK Contract Checker
  │     └── core/contract_checker.py
  ├── Memory Diagnostics
  │     └── core/api_client.py
  ├── Summary Grounding Lab
  │     └── core/grounding_checker.py
  └── Reports (session state + JSON download)
```

## Components

### `app.py`
Defines navigation, the Streamlit interface, form state, chart specifications, session report history, and JSON download actions. API requests and heuristic analysis are delegated to core modules.

### `memory_doctor/core/contract_checker.py`
Loads and inspects OpenAPI data, normalizes route paths, statically extracts supported route patterns from Python source, and compares detected routes to the selected specification. Static scanning is intentionally non-executing.

### `memory_doctor/core/api_client.py`
Contains the read-only HTTP diagnostics for the fixed TinyHumans API host: public health and memory-event access. Requests have a timeout and a custom Memory Doctor User-Agent. Redirects are not followed to avoid forwarding credentials to another location. The memory request uses the configured authentication style; the app currently presents the check as a bearer-authenticated probe.

### `memory_doctor/core/grounding_checker.py`
Runs local text heuristics over a source and summary. It counts words and checks candidate entities, dates, numbers, and required phrases. It returns JSON-serializable findings and limitations.

### `tests/`
Contains standard-library `unittest` tests for the contract checker and grounding checker. Tests are local unit tests; they do not exercise the hosted API.

## Data flow

### Contract comparison
OpenAPI JSON + SDK source → parse specification → statically extract candidate routes → normalize and compare → display results → optionally export JSON.

### Live diagnostics
User clicks a check → read-only HTTP request → normalized status and safe message → session result → JSON report without credentials.

### Grounding inspection
User supplies source, summary, optional required phrases → local heuristic checks → findings and descriptive charts → JSON report without source/summary text.

## State and persistence

The app uses Streamlit session state for the latest results and report history. This state is session-scoped; it is not a persistent database. Uploaded files and entered text are processed for the current app interaction. Reports should be treated as user-generated diagnostic artifacts.

## Trust boundaries

- Uploaded Python code is parsed, not executed.
- The API client calls a fixed host rather than an arbitrary user-supplied URL.
- Live API results are dependent on network conditions, endpoint behavior, authentication, and account entitlements.
- Grounding results are lexical signals and do not establish semantic correctness.
