# User Guide

## Start the app
From the repository root, create a virtual environment, install dependencies, and launch Streamlit. The exact commands are in the main README.

## SDK Contract Checker

1. Upload a Swagger/OpenAPI JSON file representing the contract you want to compare against.
2. Inspect the documented endpoints using the searchable endpoint list.
3. Choose one source mode:
   - **Installed tinyhumansai package:** scans Python source files in the package installed in the same environment that runs Streamlit.
   - **Upload Python files:** select one or more `.py` files containing SDK request or route construction logic.
4. Run or refresh the comparison. The app also refreshes when it detects changed inputs.
5. Review detected routes and the comparison table. Download the JSON report if you need to share the result.

The scanner uses static Python AST inspection. Uploading a source file does not execute it. Only a subset of route-construction patterns can be recognized.

## Memory Diagnostics

### API connectivity
Runs a keyless, read-only `GET /health` request. A successful response confirms that this endpoint responded; it is not an end-to-end memory test.

### Memory API access
Enter a dashboard API key in the masked field and run the read-only `GET /memory/events` check. The key is kept in the current Streamlit session to support repeated testing. Do not share it or include it in screenshots. A `401` or `403` should be interpreted as an authentication/access result, not automatically as a pipeline failure.

### Synthetic pipeline scenarios
Choose one of the supplied scenarios and run the simulated diagnostic. These examples exercise the interface and illustrate possible findings. They are not connected to a real OpenHuman workspace or TinyCortex tenant.

## Summary Grounding Lab

1. Paste the original source into **Original source**.
2. Paste the generated memory summary into **Generated memory summary**.
3. Optionally enter required phrases, one per line.
4. Select **Analyze summary**.
5. Review the findings and charts. A candidate is a prompt for human review, not a confirmed hallucination.
6. Download the JSON report if needed.

The comparison is performed locally in the app process. The exported report contains counts and findings, not the source/summary text.

## Reports

Reports are retained in Streamlit session state. They are available under Reports for the duration of that session and can be downloaded as JSON. Session history is not a durable database and may disappear when the session ends or the app restarts.
