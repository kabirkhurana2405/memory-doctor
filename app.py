
import streamlit as st
import json
from datetime import datetime, timezone
import hashlib
from importlib.metadata import PackageNotFoundError, version as package_version
from importlib.util import find_spec
from pathlib import Path

st.set_page_config(
    page_title="Memory Doctor",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",

)
from memory_doctor.core.api_client import (
    check_api_reachability,
    check_memory_access,
)



from memory_doctor.core.contract_checker import (
    load_spec,
    get_operations,
    check_route,
    extract_sdk_routes,
    compare_routes,
)
from memory_doctor.core.grounding_checker import analyze_summary
# --------------------------------------------------
# BLACK BACKGROUND / WHITE TEXT
# --------------------------------------------------

st.markdown("""
<style>
    /* Global background */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stHeader"] {
        background: #000000 !important;
        color: #FFFFFF !important;
    }

    .block-container {
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        padding: 1.5rem clamp(1rem, 2vw, 2rem) 3rem !important;
        overflow-x: hidden;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #000000 !important;
        border-right: 1px solid #333333;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    /* All text */
    h1, h2, h3, h4, h5, h6,
    p, label, span, li,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }

    /* Hero */
    .hero {
        background: #000000;
        border: 1px solid #444444;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        width: 100%;
        box-sizing: border-box;
    }

    .hero h1 {
        color: #FFFFFF !important;
        font-size: clamp(1.6rem, 3vw, 2rem);
        font-weight: 700;
        margin: 0 0 .5rem 0;
    }

    .hero p {
        color: #CCCCCC !important;
        font-size: .95rem;
        margin: 0;
    }

    .eyebrow {
        color: #FFFFFF !important;
        font-size: .72rem;
        font-weight: 700;
        letter-spacing: .1em;
        text-transform: uppercase;
        margin-bottom: .6rem;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #000000 !important;
        border: 1px solid #444444 !important;
        border-radius: 10px;
        padding: 1rem;
        min-width: 0;
        box-sizing: border-box;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"] {
        color: #FFFFFF !important;
    }

    /* General cards */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #000000 !important;
        border: 1px solid #444444 !important;
        border-radius: 10px;
    }

    /* High-contrast buttons: dark text on a light surface.
       Explicitly style inner spans because the global text rule above
       otherwise forces button labels to white. */
    div[data-testid="stButton"] button,
    div[data-testid="stFormSubmitButton"] button,
    div[data-testid="stDownloadButton"] button {
        background: #F3F4F6 !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 8px !important;
        font-weight: 650 !important;
        transition: background .15s ease, border-color .15s ease;
    }

    div[data-testid="stButton"] button span,
    div[data-testid="stFormSubmitButton"] button span,
    div[data-testid="stDownloadButton"] button span,
    div[data-testid="stButton"] button p,
    div[data-testid="stFormSubmitButton"] button p,
    div[data-testid="stDownloadButton"] button p {
        color: #111827 !important;
    }

    div[data-testid="stButton"] button:hover,
    div[data-testid="stFormSubmitButton"] button:hover,
    div[data-testid="stDownloadButton"] button:hover {
        background: #D1D5DB !important;
        color: #111827 !important;
        border-color: #9CA3AF !important;
    }

    div[data-testid="stButton"] button:focus-visible,
    div[data-testid="stFormSubmitButton"] button:focus-visible,
    div[data-testid="stDownloadButton"] button:focus-visible {
        outline: 3px solid #38BDF8 !important;
        outline-offset: 2px;
        box-shadow: none !important;
    }

    div[data-testid="stButton"] button:disabled,
    div[data-testid="stFormSubmitButton"] button:disabled,
    div[data-testid="stDownloadButton"] button:disabled {
        background: #4B5563 !important;
        color: #F9FAFB !important;
        border-color: #6B7280 !important;
        opacity: 1 !important;
    }

    /* File uploaders: visible drop zone and high-contrast browse button. */
    [data-testid="stFileUploaderDropzone"] {
        background: #101010 !important;
        border: 1px dashed #777777 !important;
        border-radius: 10px !important;
    }

    [data-testid="stFileUploaderDropzone"] * {
        color: #F9FAFB !important;
    }

    [data-testid="stFileUploaderDropzone"] button {
        background: #E5E7EB !important;
        color: #111827 !important;
        border: 1px solid #9CA3AF !important;
        border-radius: 7px !important;
        font-weight: 650 !important;
    }

    [data-testid="stFileUploaderDropzone"] button span,
    [data-testid="stFileUploaderDropzone"] button p {
        color: #111827 !important;
    }

    [data-testid="stFileUploaderFile"] {
        background: #171717 !important;
        border: 1px solid #444444 !important;
        border-radius: 7px !important;
    }

    [data-testid="stFileUploaderFile"] * {
        color: #F9FAFB !important;
    }

    /* Inputs */
    input, textarea,
    [data-baseweb="input"],
    [data-baseweb="select"] > div {
        background: #000000 !important;
        color: #FFFFFF !important;
        border-color: #555555 !important;
    }

    input::placeholder,
    textarea::placeholder {
        color: #999999 !important;
    }

    /* Radio buttons and checkboxes */
    [data-testid="stRadio"] label,
    [data-testid="stCheckbox"] label {
        color: #FFFFFF !important;
    }

    /* Alerts and notices */
    [data-testid="stAlert"] {
        background: #000000 !important;
        border: 1px solid #666666 !important;
        color: #FFFFFF !important;
    }

    [data-testid="stAlert"] p {
        color: #FFFFFF !important;
    }

    /* Dividers */
    hr {
        border-color: #333333 !important;
    }

    /* Captions */
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {
        color: #AAAAAA !important;
    }

    /* Responsive layout */
    @media (max-width: 700px) {
        .block-container {
            padding: 1rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

PAGES = [
    "Overview",
    "SDK Contract Checker",
    "Memory Diagnostics",
    "Summary Grounding Lab",
    "Reports",
]

if "workspace" not in st.session_state:
    st.session_state.workspace = "Overview"


def navigate(page):
    st.session_state.workspace = page


if "sdk_upload_generation" not in st.session_state:
    st.session_state.sdk_upload_generation = 0


def reset_sdk_uploads():
    """Remount SDK upload widgets and clear the currently displayed comparison."""
    st.session_state.sdk_upload_generation += 1
    st.session_state.pop("sdk_report", None)


# Reports and test results persist across Streamlit reruns within this session.
# They are intentionally session-only; no API credentials are stored in reports.
if "report_history" not in st.session_state:
    st.session_state.report_history = []


def remember_report(category, title, payload, filename):
    """Save a report once per run, keeping a bounded session history."""
    generated_at = payload.get("generated_at") or datetime.now(
        timezone.utc
    ).isoformat(timespec="microseconds")
    report_payload = dict(payload)
    report_payload.setdefault("generated_at", generated_at)
    fingerprint = hashlib.sha256(
        (
            category
            + generated_at
            + json.dumps(report_payload, sort_keys=True, default=str)
        ).encode("utf-8")
    ).hexdigest()[:16]

    history = st.session_state.report_history
    if any(item.get("id") == fingerprint for item in history):
        return

    history.insert(0, {
        "id": fingerprint,
        "category": category,
        "title": title,
        "generated_at": generated_at,
        "filename": filename,
        "payload": report_payload,
    })
    st.session_state.report_history = history[:50]


def grounding_chart_data(result):
    """Build transparent chart values from heuristic results."""
    return {
        "word_counts": {
            "source": result["source_word_count"],
            "summary": result["summary_word_count"],
        },
        "review_candidates_by_check": {
            "Length expansion": int(bool(result["expanded"])),
            "Unsupported entities": len(result["unsupported_entities"]),
            "Unsupported dates": len(result["unsupported_dates"]),
            "Unsupported numbers": len(result["unsupported_numbers"]),
            "Missing required phrases": len(result["missing_required_phrases"]),
        },
    }


with st.sidebar:
    st.markdown("### Memory Doctor")
    st.caption("Memory QA & developer tools")
    st.divider()

    st.radio(
        "Workspace",
        PAGES,
        key="workspace",
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("ENVIRONMENT")
    st.markdown("Local application")
    st.caption("Local app · Live API checks available")


page = st.session_state.workspace


# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

if page == "Overview":

    st.markdown("""
    <div class="hero">
        <div class="eyebrow">DEVELOPER TOOLS</div>
        <h1>Memory Doctor</h1>
        <p>
            Diagnose memory issues, validate API contracts
            and generate actionable reports.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Overview")
    report_history = st.session_state.get("report_history", [])
    sdk_checks = sum(item.get("category") == "sdk" for item in report_history)
    memory_checks = sum(
        item.get("category") in ("memory_live", "memory_simulated", "memory_grounding")
        for item in report_history
    )

    st.caption("Counts reflect checks saved in this browser session.")
    c1, c2, c3 = st.columns(3, gap="small")

    with c1:
        st.metric("SDK checks", sdk_checks)

    with c2:
        st.metric("Memory checks", memory_checks)

    with c3:
        st.metric("Reports", len(report_history))

    st.divider()
    st.subheader("Diagnostic tools")
    st.caption("Select a tool to get started.")

    left, right = st.columns(2, gap="medium")

    with left:
        with st.container(border=True):
            st.markdown("### SDK Contract Checker")
            st.write(
                "Compare SDK routes and request formats "
                "against a published OpenAPI specification."
            )
            st.caption("Python · OpenAPI · API validation")

            st.button(
                "Open checker →",
                key="open_checker",
                type="primary",
                use_container_width=True,
                on_click=navigate,
                args=("SDK Contract Checker",),
            )

    with right:
        with st.container(border=True):
            st.markdown("### Memory Diagnostics")
            st.write(
                "Inspect ingestion, embeddings, extraction, "
                "summarisation and retrieval."
            )
            st.caption("Memory health · Recovery · Testing")

            st.button(
                "Open diagnostics →",
                key="open_diagnostics",
                use_container_width=True,
                on_click=navigate,
                args=("Memory Diagnostics",),
            )

    with st.container(border=True):
        st.markdown("### Summary Grounding Lab")
        st.write(
            "Check generated memory summaries for expansion, "
            "unsupported entity/date/number candidates, and missing key phrases."
        )
        st.caption("Local heuristic QA · Source-to-summary review")
        st.button(
            "Open grounding lab →",
            key="open_grounding_lab",
            use_container_width=True,
            on_click=navigate,
            args=("Summary Grounding Lab",),
        )


# --------------------------------------------------
# SDK CONTRACT CHECKER
# --------------------------------------------------




elif page == "SDK Contract Checker":

    st.title("SDK Contract Checker")
    st.caption("Inspect Python SDK routes against a selected API contract.")
    st.divider()

    upload_generation = st.session_state.sdk_upload_generation

    with st.container(border=True):
        st.markdown("### 1. API specification")
        st.caption(
            "Upload the Swagger/OpenAPI JSON that the SDK should follow. "
            "Results refresh when the specification or SDK source changes."
        )
        uploaded = st.file_uploader(
            "OpenAPI specification (.json)",
            type=["json"],
            key=f"swagger_upload_{upload_generation}",
            help="Choose the contract for the SDK version you are inspecting.",
        )

    if uploaded is None:
        st.info("Upload an OpenAPI JSON specification to begin.")
    else:
        try:
            spec_data = uploaded.getvalue()
            spec = load_spec(spec_data)
            paths = spec["paths"]
            spec_hash = hashlib.sha256(spec_data).hexdigest()

            st.success(f"Specification loaded: {uploaded.name}")
            operations = get_operations(paths)
            c1, c2, c3 = st.columns(3)
            c1.metric("Paths", len(paths))
            c2.metric("Operations", len(operations))
            c3.metric("OpenAPI", str(spec.get("openapi", "Unknown")))

            with st.expander("View documented endpoints"):
                search = st.text_input(
                    "Search endpoints",
                    placeholder="/memory/",
                    key="endpoint_search",
                )
                filtered = [
                    op for op in operations
                    if search.lower() in (
                        op["Path"] + " " + op["Method"] + " " + op["Summary"]
                    ).lower()
                ]
                st.dataframe(filtered, use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("2. SDK source")
            st.caption(
                "Choose the installed package for a direct local inspection, "
                "or upload selected Python source files. Static analysis only: "
                "SDK code is never executed. Do not upload secrets."
            )

            source_mode = st.radio(
                "Source to inspect",
                ["Installed tinyhumansai package", "Upload Python files"],
                horizontal=True,
                key="sdk_source_mode",
            )

            sdk_sources = []
            source_errors = []
            sdk_version = "not available"
            source_description = ""

            if source_mode == "Installed tinyhumansai package":
                try:
                    package_spec = find_spec("tinyhumansai")
                except (ImportError, ModuleNotFoundError, ValueError) as exc:
                    package_spec = None
                    source_errors.append(f"Could not locate package: {exc}")

                if package_spec is not None:
                    try:
                        sdk_version = package_version("tinyhumansai")
                    except PackageNotFoundError:
                        sdk_version = "version metadata unavailable"

                    roots = [
                        Path(location)
                        for location in (package_spec.submodule_search_locations or [])
                    ]
                    if not roots and package_spec.origin:
                        roots = [Path(package_spec.origin).parent]

                    package_files = []
                    for root in roots:
                        if root.is_dir():
                            package_files.extend(
                                path for path in root.rglob("*.py")
                                if "__pycache__" not in path.parts
                                and "tests" not in {part.lower() for part in path.parts}
                                and not path.name.startswith("test_")
                            )

                    package_files = sorted(set(package_files), key=lambda p: str(p).lower())
                    if not package_files:
                        source_errors.append(
                            "The package was found, but no Python source files were available to inspect."
                        )

                    total_bytes = 0
                    for path in package_files[:200]:
                        try:
                            data = path.read_bytes()
                        except OSError as exc:
                            source_errors.append(f"Could not read {path.name}: {exc}")
                            continue

                        if len(data) > 2 * 1024 * 1024:
                            source_errors.append(
                                f"{path.name}: skipped because it exceeds the 2 MB per-file limit."
                            )
                            continue
                        if total_bytes + len(data) > 20 * 1024 * 1024:
                            source_errors.append(
                                "Stopped after the 20 MB total source limit."
                            )
                            break

                        relative_name = next(
                            (path.relative_to(root).as_posix() for root in roots
                             if path.is_relative_to(root)),
                            path.name,
                        )
                        sdk_sources.append({"name": relative_name, "data": data})
                        total_bytes += len(data)

                    if len(package_files) > 200:
                        source_errors.append(
                            "Only the first 200 package Python files were inspected."
                        )
                    source_description = f"tinyhumansai {sdk_version} · {len(sdk_sources)} source file(s)"
                else:
                    st.warning(
                        "tinyhumansai is not installed in the Python environment "
                        "running this Streamlit app. Switch to uploaded files or "
                        "install the package in this environment."
                    )
            else:
                sdk_files = st.file_uploader(
                    "Python SDK source files (.py)",
                    type=["py"],
                    accept_multiple_files=True,
                    key=f"sdk_files_{upload_generation}",
                    help=(
                        "Select the SDK HTTP client or modules that build API requests. "
                        "You can select multiple .py files at once; each is limited to 2 MB."
                    ),
                )

                if sdk_files:
                    for file in sdk_files:
                        sdk_sources.append({"name": file.name, "data": file.getvalue()})
                    st.success(f"{len(sdk_files)} Python file(s) selected")
                    st.dataframe(
                        [
                            {"File": file.name, "Size": f"{file.size:,} bytes"}
                            for file in sdk_files
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )
                    source_description = f"Uploaded source · {len(sdk_files)} file(s)"
                else:
                    st.info("Select one or more Python source files to inspect.")

                st.button(
                    "Clear uploaded files and comparison",
                    key="clear_sdk_uploads",
                    on_click=reset_sdk_uploads,
                    use_container_width=True,
                    help="Clear both uploads and remove the comparison currently shown. Saved reports remain in Reports.",
                )

            for error in source_errors:
                st.warning(error)

            source_digest = hashlib.sha256()
            source_digest.update(source_mode.encode("utf-8"))
            source_digest.update(sdk_version.encode("utf-8"))
            for source in sorted(sdk_sources, key=lambda item: item["name"].lower()):
                source_digest.update(source["name"].encode("utf-8"))
                source_digest.update(b"\0")
                source_digest.update(source["data"])
            source_hash = source_digest.hexdigest()
            input_fingerprint = hashlib.sha256(
                f"{spec_hash}:{source_hash}".encode("utf-8")
            ).hexdigest()

            saved_before_run = st.session_state.get("sdk_report")
            inputs_changed = (
                bool(sdk_sources)
                and (
                    saved_before_run is None
                    or saved_before_run.get("input_fingerprint") != input_fingerprint
                )
            )

            st.caption(f"Selected source: {source_description or 'No source selected'}")
            if sdk_sources:
                st.caption(f"Source fingerprint: {source_hash[:12]} ·{'' if not inputs_changed else ' Changed inputs detected'}")

            run_clicked = st.button(
                "Run / refresh SDK comparison",
                key="inspect_and_compare_sdk",
                type="primary",
                use_container_width=True,
                disabled=not bool(sdk_sources),
                help="Runs again when the selected specification or SDK source changes.",
            )

            # Automatically refresh if the selected contract or source changes.
            if sdk_sources and (inputs_changed or run_clicked):
                detected = []
                errors = list(source_errors)
                for source in sdk_sources:
                    try:
                        text_source = source["data"].decode("utf-8-sig")
                        detected.extend(
                            extract_sdk_routes(text_source, source["name"])
                        )
                    except (UnicodeDecodeError, ValueError, RecursionError, SyntaxError) as exc:
                        errors.append(f"{source['name']}: {exc}")

                results = compare_routes(paths, detected)
                generated_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
                st.session_state.sdk_report = {
                    "spec_hash": spec_hash,
                    "source_hash": source_hash,
                    "input_fingerprint": input_fingerprint,
                    "filename": uploaded.name,
                    "source_mode": source_mode,
                    "source_description": source_description,
                    "sdk_version": sdk_version,
                    "source_files": [item["name"] for item in sdk_sources],
                    "detected": detected,
                    "results": results,
                    "errors": errors,
                    "generated_at": generated_at,
                }

                sdk_export = {
                    "report_type": "sdk_contract_check",
                    "generated_at": generated_at,
                    "specification": uploaded.name,
                    "source_mode": source_mode,
                    "sdk_version": sdk_version,
                    "source_files": [item["name"] for item in sdk_sources],
                    "routes": results,
                    "errors": errors,
                    "limitations": [
                        "Static inspection does not execute SDK code.",
                        "Dynamically constructed routes may be missed.",
                        "Missing from the specification does not prove the live endpoint is unavailable.",
                    ],
                }
                remember_report("sdk", "SDK contract comparison", sdk_export, "sdk-contract-report.json")

            saved = st.session_state.get("sdk_report")
            is_current = (
                saved is not None
                and saved.get("input_fingerprint") == input_fingerprint
            )

            if is_current:
                st.divider()
                st.subheader("Inspection results")
                st.caption(
                    "Results match the currently selected files. "
                    f'Last analyzed: {saved.get("generated_at", "Unknown")} · '
                    f'{saved.get("source_description", "Source not recorded")}'
                )
                for error in saved["errors"]:
                    st.warning(error)

                detected = saved["detected"]
                results = saved["results"]
                a, b, c = st.columns(3)
                a.metric("Routes detected", len(detected))
                b.metric("Documented", sum(r["Status"] == "Found" for r in results))
                c.metric(
                    "Not in specification",
                    sum(r["Status"] == "Not in specification" for r in results),
                )

                if detected:
                    st.markdown("**Detected SDK routes**")
                    st.dataframe(detected, use_container_width=True, hide_index=True)
                    st.markdown("**Contract comparison**")
                    st.dataframe(results, use_container_width=True, hide_index=True)
                elif not saved["errors"]:
                    st.warning(
                        "No statically identifiable routes found. Try inspecting "
                        "the SDK's HTTP client module or another source file that "
                        "constructs API requests."
                    )

                report = {
                    "specification": saved["filename"],
                    "source_mode": saved["source_mode"],
                    "sdk_version": saved["sdk_version"],
                    "source_files": saved["source_files"],
                    "generated_at": saved.get("generated_at"),
                    "routes": results,
                    "errors": saved["errors"],
                    "limitations": [
                        "Static inspection does not execute SDK code.",
                        "Dynamically constructed routes may be missed.",
                        "Missing from the specification does not prove the live endpoint is unavailable.",
                    ],
                }
                st.download_button(
                    "Download JSON report",
                    data=json.dumps(report, indent=2),
                    file_name="sdk-contract-report.json",
                    mime="application/json",
                )
            elif saved:
                st.info(
                    "The previous comparison is not being shown because the selected "
                    "specification or source has changed. A fresh comparison will "
                    "run when source files are available."
                )

        except (ValueError, TypeError, KeyError, UnicodeDecodeError) as exc:
            st.error(f"Could not load specification: {exc}")

    st.divider()
    st.button(
        "← Back to overview",
        on_click=navigate,
        args=("Overview",),
    )
# --------------------------------------------------
# MEMORY DIAGNOSTICS
# --------------------------------------------------

elif page == "Memory Diagnostics":

    st.title("Memory Diagnostics")
    st.caption(
        "Inspect memory readiness, diagnose pipeline failures "
        "and test API accessibility."
    )
    st.divider()

    # --------------------------------------------------
    # LIVE API CHECKS
    # --------------------------------------------------

    st.subheader("Live API checks")
    st.caption(
        "Read-only checks against the hosted TinyHumans API. "
        "These do not create, retrieve or modify memories."
    )

    # Public API health check (no key required)
    with st.container(border=True):
        st.markdown("### API connectivity")
        st.write(
            "Check whether the public TinyHumans API health endpoint responds."
        )

        if st.button(
            "Check API connectivity",
            key="run_live_connectivity",
            use_container_width=True,
        ):
            with st.spinner("Checking API connectivity..."):
                result = check_api_reachability()
                st.session_state.live_connectivity_result = result
                connectivity_export = {
                    "report_type": "api_connectivity_check",
                    "generated_at": datetime.now(
                        timezone.utc
                    ).isoformat(timespec="microseconds"),
                    "endpoint": "/health",
                    "credentials_included": False,
                    "result": {
                        key: result.get(key)
                        for key in (
                            "reachable",
                            "ok",
                            "status_code",
                            "latency_ms",
                            "message",
                        )
                    },
                }
                remember_report(
                    "memory_live",
                    "API connectivity check",
                    connectivity_export,
                    "api-connectivity-report.json",
                )

        connectivity = st.session_state.get("live_connectivity_result")

        if connectivity:
            if connectivity["ok"]:
                st.success("Connectivity successful")
            elif connectivity["reachable"]:
                st.warning("The API responded, but the request was unsuccessful.")
            else:
                st.error("Could not connect to the API.")

            a, b = st.columns(2)
            a.metric(
                "HTTP status",
                str(connectivity["status_code"] or "N/A"),
            )
            b.metric(
                "Latency",
                f'{connectivity["latency_ms"]} ms',
            )
            st.caption(connectivity["message"])

    # Authenticated, read-only memory access
    with st.container(border=True):
        st.markdown("### Memory API access")
        st.write(
            "Check whether your API key can access "
            "the read-only memory events endpoint."
        )
        st.caption(
            "Your key is entered locally and is not included "
            "in diagnostic reports."
        )

        with st.form("memory_access_form", clear_on_submit=False):
            api_key = st.text_input(
                "Dashboard API key",
                type="password",
                placeholder="Enter your API key",
                key="memory_api_key_input",
                help=(
                    "The key stays masked and is retained only in this "
                    "Streamlit session so you can rerun the check. "
                    "It is never included in reports."
                ),
            )
            submitted = st.form_submit_button(
                "Check memory access",
                key="run_memory_access",
                use_container_width=True,
            )

        if submitted:
            if not api_key.strip():
                st.session_state.memory_access_error = (
                    "Please enter an API key. The previous result has been retained."
                )
            else:
                st.session_state.memory_access_error = None
                with st.spinner("Checking memory access..."):
                    result = check_memory_access(api_key)
                    st.session_state.memory_access_result = result

                memory_export = {
                    "report_type": "memory_access_check",
                    "generated_at": datetime.now(
                        timezone.utc
                    ).isoformat(timespec="microseconds"),
                    "endpoint": "/memory/events",
                    "auth_method": "Bearer",
                    "credentials_included": False,
                    "result": {
                        key: result.get(key)
                        for key in (
                            "reachable",
                            "ok",
                            "status_code",
                            "latency_ms",
                            "message",
                        )
                    },
                    "limitations": [
                        "This is a read-only authorization check.",
                        "A successful response does not prove ingestion works.",
                        "A 401 or 403 does not prove the memory pipeline is broken.",
                    ],
                }
                remember_report(
                    "memory_live",
                    "Memory API access check",
                    memory_export,
                    "memory-access-report.json",
                )

        access_error = st.session_state.get("memory_access_error")
        if access_error:
            st.warning(access_error)

        memory_access = st.session_state.get("memory_access_result")

        if memory_access:
            status = memory_access.get("status_code")
            if memory_access["ok"]:
                st.success("Memory API access granted")
            elif status == 401:
                st.warning(
                    "Authentication failed. Check the key and the "
                    "authentication method."
                )
            elif status == 403:
                st.warning(
                    "Access denied. The server responded, but this key "
                    "is not authorized for the endpoint. This may reflect "
                    "a missing permission or hosted-alpha restriction; "
                    "it is not evidence of a memory pipeline failure."
                )
            elif memory_access["reachable"]:
                st.warning("The API responded, but the memory request failed.")
            else:
                st.error("Could not connect to the memory endpoint.")

            a, b = st.columns(2)
            a.metric(
                "HTTP status",
                str(status or "N/A"),
            )
            b.metric(
                "Latency",
                f'{memory_access["latency_ms"]} ms',
            )
            st.caption(memory_access["message"])

    # Safe live diagnostic export
    connectivity = st.session_state.get("live_connectivity_result")
    memory_access = st.session_state.get("memory_access_result")

    if connectivity or memory_access:
        live_report = {
            "report_type": "live_api_diagnostics",
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "credentials_included": False,
            "connectivity": (
                {
                    key: connectivity.get(key)
                    for key in (
                        "reachable",
                        "ok",
                        "status_code",
                        "latency_ms",
                    )
                }
                if connectivity else None
            ),
            "memory_access": (
                {
                    key: memory_access.get(key)
                    for key in (
                        "reachable",
                        "ok",
                        "status_code",
                        "latency_ms",
                    )
                }
                if memory_access else None
            ),
            "limitations": [
                "Only read-only API endpoints were checked.",
                "Successful API access does not prove "
                "that memory ingestion works.",
                "No memory data was retrieved or modified.",
            ],
        }

        st.download_button(
            "Download live API report (JSON)",
            data=json.dumps(live_report, indent=2),
            file_name="live-api-diagnostics.json",
            mime="application/json",
            use_container_width=True,
        )

    st.divider()

    # --------------------------------------------------
    # SIMULATED MEMORY DIAGNOSTICS
    # --------------------------------------------------

    st.subheader("Memory pipeline diagnostics")
    st.caption(
        "Synthetic scenarios for testing the diagnostic "
        "interface. These are not live memory results."
    )

    scenarios = {
        "Healthy memory pipeline": {
            "readiness": "Searchable",
            "stages": [
                ("Source sync", "PASS", "4 source items received."),
                ("Ingestion", "PASS", "4 chunks committed."),
                ("Embeddings", "PASS", "4 of 4 vectors generated."),
                ("Extraction", "PASS", "Entity extraction completed."),
                ("Summarisation", "PASS", "Summary refreshed."),
                ("Retrieval", "PASS", "Test query returned 1 result."),
            ],
            "actions": [
                "No issues detected in this sample."
            ],
        },
        "Synced but not searchable": {
            "readiness": "Not searchable",
            "stages": [
                ("Source sync", "PASS", "4 source items received."),
                ("Ingestion", "PASS", "4 chunks committed."),
                ("Embeddings", "WARN", "Only 0 of 4 vectors available."),
                ("Extraction", "SKIPPED", "Awaiting pipeline processing."),
                ("Summarisation", "SKIPPED", "Awaiting pipeline processing."),
                ("Retrieval", "FAIL", "Test query returned 0 results."),
            ],
            "actions": [
                "Inspect the embedding worker and its queue.",
                "Verify that vectors were written to the index.",
                "Retry failed indexing jobs if safe.",
                "Repeat the retrieval test after processing.",
            ],
        },
        "Embedding worker failure": {
            "readiness": "Blocked before retrieval",
            "stages": [
                ("Source sync", "PASS", "4 source items received."),
                ("Ingestion", "PASS", "4 chunks committed."),
                ("Embeddings", "FAIL", "Embedding generation failed."),
                ("Extraction", "SKIPPED", "Processing was interrupted."),
                ("Summarisation", "SKIPPED", "Processing was interrupted."),
                ("Retrieval", "SKIPPED", "No retrieval test performed."),
            ],
            "actions": [
                "Inspect the embedding worker error logs.",
                "Check embedding provider availability.",
                "Retry failed jobs after identifying the cause.",
                "Verify the index before testing retrieval.",
            ],
        },
        "Retrieval failure": {
            "readiness": "Retrieval unverified",
            "stages": [
                ("Source sync", "PASS", "4 source items received."),
                ("Ingestion", "PASS", "4 chunks committed."),
                ("Embeddings", "PASS", "4 of 4 vectors generated."),
                ("Extraction", "PASS", "Entity extraction completed."),
                ("Summarisation", "PASS", "Summary refreshed."),
                ("Retrieval", "FAIL", "Test query returned 0 results."),
            ],
            "actions": [
                "Verify the retrieval query and its scope.",
                "Check index freshness and indexing completion.",
                "Inspect similarity thresholds and filters.",
                "Repeat retrieval using a known test query.",
            ],
        },
    }

    selected = st.selectbox(
        "Choose a test scenario",
        list(scenarios.keys()),
        key="memory_scenario",
    )

    if st.button(
        "Run simulated diagnostic",
        key="run_memory_diagnostic",
        type="primary",
        use_container_width=True,
    ):
        sample = scenarios[selected]

        st.session_state.memory_result = {
            "scenario": selected,
            "readiness": sample["readiness"],
            "stages": sample["stages"],
            "actions": sample["actions"],
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

    result = st.session_state.get("memory_result")

    # Keep the latest result visible even if the selector changes.
    if result:
        st.divider()
        st.subheader("Diagnostic results")

        st.caption(
            f'Scenario: {result["scenario"]} · '
            f'Simulated · {result["generated_at"]}'
        )

        st.markdown("### Memory readiness")
        st.markdown(f'**{result["readiness"]}**')

        passed = sum(
            stage[1] == "PASS" for stage in result["stages"]
        )
        warnings = sum(
            stage[1] == "WARN" for stage in result["stages"]
        )
        failed = sum(
            stage[1] == "FAIL" for stage in result["stages"]
        )
        skipped = sum(
            stage[1] == "SKIPPED" for stage in result["stages"]
        )

        a, b, c, d = st.columns(4)
        a.metric("Passed", passed)
        b.metric("Warnings", warnings)
        c.metric("Failed", failed)
        d.metric("Skipped", skipped)

        st.divider()
        st.markdown("### Pipeline stages")

        stage_rows = [
            {
                "Stage": name,
                "Status": status,
                "Details": details,
            }
            for name, status, details in result["stages"]
        ]

        st.dataframe(
            stage_rows,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()
        st.markdown("### Suggested recovery")

        for action in result["actions"]:
            st.markdown(f"- {action}")

        simulated_report = {
            "report_type": "memory_diagnostics",
            "mode": "simulated",
            "generated_at": result["generated_at"],
            "scenario": result["scenario"],
            "readiness": result["readiness"],
            "stages": stage_rows,
            "suggested_recovery": result["actions"],
            "limitations": [
                "This report uses synthetic demo data.",
                "No live OpenHuman memory was inspected.",
                "No memory data was modified.",
            ],
        }
        remember_report(
            "memory_simulated",
            f'Simulated diagnostic: {result["scenario"]}',
            simulated_report,
            "memory-diagnostic-report.json",
        )

        st.download_button(
            "Download simulated report (JSON)",
            data=json.dumps(simulated_report, indent=2),
            file_name="memory-diagnostic-report.json",
            mime="application/json",
            use_container_width=True,
        )

    st.divider()
    st.button(
        "← Back to overview",
        on_click=navigate,
        args=("Overview",),
    )


# --------------------------------------------------
# SUMMARY GROUNDING LAB
# --------------------------------------------------

elif page == "Summary Grounding Lab":

    st.title("Summary Grounding Lab")
    st.caption(
        "Inspect whether a generated memory summary stays close to its source."
    )
    st.info(
        "Local heuristic checks only. This feature does not call an LLM, "
        "send text to an API, or prove semantic truth. Review every flagged item."
    )

    demo_source = (
        "Project Atlas is a local-first note-taking prototype.\n"
        "Memory chunks are stored in SQLite.\n"
        "The evaluation uses five synthetic documents.\n"
        "The team has not selected a launch date."
    )
    demo_summary = (
        "Project Atlas, led by Dr. Elias Thorne and the Memory Innovation Team, "
        "is a comprehensive knowledge platform.\n"
        "It stores eight documents in SQLite and will launch on 2026-10-01.\n"
        "The Reasoning Engine will provide autonomous planning, intelligent "
        "discovery, and enterprise-grade workflows."
    )
    demo_required = (
        "The evaluation uses five synthetic documents.\n"
        "The team has not selected a launch date."
    )

    def load_grounding_example():
        st.session_state["grounding_source_input"] = demo_source
        st.session_state["grounding_summary_input"] = demo_summary
        st.session_state["grounding_required_input"] = demo_required

    if "grounding_source_input" not in st.session_state:
        load_grounding_example()

    st.caption("Example data is synthetic. Replace it with your own source and summary.")
    st.button(
        "Load synthetic example",
        key="load_grounding_example",
        on_click=load_grounding_example,
        use_container_width=False,
    )

    with st.container(border=True):
        st.markdown("### Source and generated summary")
        source_text = st.text_area(
            "Original source",
            key="grounding_source_input",
            height=220,
            help="Paste the source notes or document used to create the summary.",
        )
        summary_text = st.text_area(
            "Generated memory summary",
            key="grounding_summary_input",
            height=220,
            help="Paste the L1 or higher-level summary you want to inspect.",
        )
        required_text = st.text_area(
            "Required phrases (optional; one per line)",
            key="grounding_required_input",
            height=100,
            help=(
                "Exact normalized phrase matching is used. Paraphrases may be "
                "flagged even when their meaning is preserved."
            ),
        )
        analyze_clicked = st.button(
            "Analyze summary",
            key="analyze_grounding_summary",
            type="primary",
            use_container_width=True,
        )

    if analyze_clicked:
        try:
            analysis = analyze_summary(
                source_text,
                summary_text,
                required_text,
            )
            generated_at = datetime.now(timezone.utc).isoformat(
                timespec="microseconds"
            )
            analysis["generated_at"] = generated_at
            st.session_state.grounding_result = analysis
            st.session_state.grounding_input_hash = hashlib.sha256(
                (source_text + "\0" + summary_text + "\0" + required_text).encode("utf-8")
            ).hexdigest()

            export_payload = {
                "report_type": "summary_grounding_inspection",
                "mode": "local_heuristic",
                "generated_at": generated_at,
                "status": analysis["status"],
                "source_word_count": analysis["source_word_count"],
                "summary_word_count": analysis["summary_word_count"],
                "length_ratio": analysis["length_ratio"],
                "expanded": analysis["expanded"],
                "unsupported_entities": analysis["unsupported_entities"],
                "unsupported_dates": analysis["unsupported_dates"],
                "unsupported_numbers": analysis["unsupported_numbers"],
                "missing_required_phrases": analysis["missing_required_phrases"],
                "findings": analysis["findings"],
                "visualizations": grounding_chart_data(analysis),
                "limitations": analysis["limitations"],
                "source_text_included": False,
                "summary_text_included": False,
            }
            remember_report(
                "memory_grounding",
                "Summary grounding inspection",
                export_payload,
                "summary-grounding-report.json",
            )
        except ValueError as exc:
            st.error(str(exc))

    result = st.session_state.get("grounding_result")
    if result:
        current_hash = hashlib.sha256(
            (source_text + "\0" + summary_text + "\0" + required_text).encode("utf-8")
        ).hexdigest()
        if current_hash != st.session_state.get("grounding_input_hash"):
            st.warning(
                "Inputs have changed since the last analysis. "
                "Run Analyze summary again to refresh the results."
            )

        st.divider()
        st.subheader("Inspection results")
        if result["findings"]:
            st.warning(
                f'Review recommended · {len(result["findings"])} heuristic finding(s). '
                "These are candidates for human review, not confirmed hallucinations."
            )
        else:
            st.success(
                "No heuristic flags found. This does not prove semantic grounding."
            )

        a, b, c = st.columns(3)
        a.metric("Source words", result["source_word_count"])
        b.metric("Summary words", result["summary_word_count"])
        c.metric(
            "Summary / source",
            f'{result["length_ratio"]:.2f}×' if result["length_ratio"] is not None else "N/A",
        )


        chart_values = grounding_chart_data(result)

        st.markdown("### Summary length")
        st.caption(
            "Word counts are descriptive; a longer summary is not automatically incorrect."
        )
        word_values = [
            {"label": "Source", "value": chart_values["word_counts"]["source"]},
            {"label": "Summary", "value": chart_values["word_counts"]["summary"]},
        ]
        word_chart_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {"values": word_values},
            "mark": {"type": "bar", "cornerRadiusEnd": 4, "height": 20},
            "encoding": {
                "y": {
                    "field": "label",
                    "type": "nominal",
                    "sort": ["Source", "Summary"],
                    "axis": {
                        "title": None,
                        "labelColor": "#D4D4D8",
                        "labelFontSize": 12,
                        "domain": False,
                        "ticks": False,
                        "labelPadding": 10,
                    },
                },
                "x": {
                    "field": "value",
                    "type": "quantitative",
                    "scale": {"zero": True},
                    "axis": {
                        "title": None,
                        "labelColor": "#A1A1AA",
                        "labelFontSize": 11,
                        "gridColor": "#303036",
                        "gridOpacity": 0.85,
                        "domainColor": "#52525B",
                        "tickColor": "#52525B",
                    },
                },
                "color": {
                    "field": "label",
                    "type": "nominal",
                    "scale": {
                        "domain": ["Source", "Summary"],
                        "range": ["#71717A", "#D4D4D8"],
                    },
                    "legend": None,
                },
                "tooltip": [
                    {"field": "label", "type": "nominal", "title": "Text"},
                    {"field": "value", "type": "quantitative", "title": "Words"},
                ],
            },
            "width": "container",
            "height": {"step": 32},
            "config": {
                "background": "#000000",
                "view": {"stroke": None},
                "axis": {"labelFont": "Arial"},
            },
        }
        st.vega_lite_chart(
            word_chart_spec,
            use_container_width=True,
            theme=None,
            key="grounding_word_chart",
        )

        st.markdown("### Review candidates by check")
        st.caption(
            "Counts show heuristic flags for review, not confirmed factual errors or a grounding score."
        )
        flag_values = [
            {"label": label, "value": value}
            for label, value in chart_values["review_candidates_by_check"].items()
        ]
        flags_chart_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {"values": flag_values},
            "mark": {"type": "bar", "cornerRadiusEnd": 4, "height": 18, "color": "#A1A1AA"},
            "encoding": {
                "y": {
                    "field": "label",
                    "type": "nominal",
                    "sort": "-x",
                    "axis": {
                        "title": None,
                        "labelColor": "#D4D4D8",
                        "labelFontSize": 11,
                        "labelLimit": 220,
                        "domain": False,
                        "ticks": False,
                        "labelPadding": 10,
                    },
                },
                "x": {
                    "field": "value",
                    "type": "quantitative",
                    "scale": {"zero": True},
                    "axis": {
                        "title": None,
                        "labelColor": "#A1A1AA",
                        "labelFontSize": 11,
                        "gridColor": "#303036",
                        "gridOpacity": 0.85,
                        "domainColor": "#52525B",
                        "tickColor": "#52525B",
                    },
                },
                "tooltip": [
                    {"field": "label", "type": "nominal", "title": "Check"},
                    {"field": "value", "type": "quantitative", "title": "Candidates"},
                ],
            },
            "width": "container",
            "height": {"step": 30},
            "config": {
                "background": "#000000",
                "view": {"stroke": None},
                "axis": {"labelFont": "Arial"},
            },
        }
        st.vega_lite_chart(
            flags_chart_spec,
            use_container_width=True,
            theme=None,
            key="grounding_flags_chart",
        )

        if result["findings"]:
            st.markdown("### Findings to review")
            st.dataframe(
                result["findings"],
                use_container_width=True,
                hide_index=True,
            )
        with st.expander("How to interpret these results"):
            st.markdown(
                "- **Length:** flags a summary that is longer than its source.\n"
                "- **Entities, dates and numbers:** flags candidates in the summary "
                "that were not found in the source using conservative text patterns.\n"
                "- **Required phrases:** checks exact normalized phrase presence; "
                "a valid paraphrase can be flagged.\n"
                "- **No heuristic flags is not a pass:** semantic entailment, context, "
                "negation and factual truth still require review."
            )

        export_payload = {
            "report_type": "summary_grounding_inspection",
            "mode": "local_heuristic",
            "generated_at": result["generated_at"],
            "status": result["status"],
            "source_word_count": result["source_word_count"],
            "summary_word_count": result["summary_word_count"],
            "length_ratio": result["length_ratio"],
            "expanded": result["expanded"],
            "unsupported_entities": result["unsupported_entities"],
            "unsupported_dates": result["unsupported_dates"],
            "unsupported_numbers": result["unsupported_numbers"],
            "missing_required_phrases": result["missing_required_phrases"],
            "findings": result["findings"],
            "visualizations": grounding_chart_data(result),
            "limitations": result["limitations"],
            "source_text_included": False,
            "summary_text_included": False,
        }
        st.download_button(
            "Download grounding report (JSON)",
            data=json.dumps(export_payload, indent=2),
            file_name="summary-grounding-report.json",
            mime="application/json",
            use_container_width=True,
            key="download_grounding_report",
        )

    st.divider()
    st.button(
        "← Back to overview",
        key="grounding_back_to_overview",
        on_click=navigate,
        args=("Overview",),
    )


# --------------------------------------------------
# REPORTS
# --------------------------------------------------

elif page == "Reports":

    st.markdown(
        '<div class="eyebrow">EXPORT CENTRE</div>',
        unsafe_allow_html=True,
    )
    st.title("Diagnostic Reports")
    st.caption(
        "Review and download generated diagnostic reports. "
        "History is retained for this Streamlit session."
    )

    report_history = st.session_state.get("report_history", [])
    if not report_history:
        st.info("No reports have been generated in this session yet.")
    else:
        st.caption(f"{len(report_history)} report(s) available in this session.")
        for index, item in enumerate(report_history):
            with st.container(border=True):
                st.markdown(f'### {item["title"]}')
                st.caption(
                    f'{item["category"]} · {item["generated_at"]}'
                )
                st.download_button(
                    "Download JSON",
                    data=json.dumps(item["payload"], indent=2),
                    file_name=item["filename"],
                    mime="application/json",
                    key=f'report_download_{item["id"]}_{index}',
                )

    st.divider()
    st.button(
        "← Back to overview",
        on_click=navigate,
        args=("Overview",),
    )
