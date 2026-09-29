# Security Notes

## API keys
- Never commit API keys, bearer tokens, `.env` files, or Streamlit secrets.
- The memory access field is masked. The key is retained in Streamlit session state to support repeated checks; clear the browser session when finished on a shared device.
- Do not include credentials in bug reports, terminal screenshots, recordings, or shared JSON.
- If a key is exposed, revoke it in the provider dashboard and generate a replacement.

## Uploaded source
The SDK Contract Checker statically parses uploaded Python files; it does not execute them. Nevertheless, source files can contain proprietary information or credentials. Upload only material you are authorized to share.

## Grounding inputs
The Summary Grounding Lab performs local heuristic processing in the running app. Do not paste customer data, private conversations, or sensitive memory exports into a shared or hosted deployment unless you have authorization and understand the hosting environment.

Grounding JSON exports omit the complete source and summary fields. Findings may still contain candidate entity strings or required phrases, so inspect exports before sharing.

## Deployment
This prototype is designed for local use. Before exposing it publicly, review Streamlit's deployment and secrets guidance, add authentication if required, and assess the risk of processing untrusted uploads and sensitive inputs.
