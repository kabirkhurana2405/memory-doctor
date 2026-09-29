# Limitations and Interpretation

Memory Doctor is an independent prototype. Its results should be read as diagnostic evidence with explicit scope, not as a general correctness verdict.

## SDK Contract Checker
- Static inspection recognizes only supported Python route-construction patterns.
- Dynamically composed paths, reflection, wrappers, generated clients, or routes assembled across modules may be missed.
- A route missing from an OpenAPI document is a contract discrepancy, not proof that the live server returns 404.
- A detected route does not prove that the operation's parameters, payload, permissions, or runtime behavior are correct.
- The comparison is only as relevant as the specification selected by the user. Version mismatches can produce misleading discrepancies.

## Live API diagnostics
- `GET /health` tests only the health endpoint.
- `GET /memory/events` is a read-only access probe; it does not prove write, ingestion, summarization, or recall functionality.
- A `401` or `403` can arise from authentication configuration, insufficient permissions, allowlisting, alpha access, or service policy. Do not label it a memory-pipeline failure without further evidence.
- HTTP status and latency are observations at the time of the test. They can vary.
- The API check is not a full service-level monitoring system.

## Synthetic memory scenarios
- Synthetic scenarios are static examples intended to exercise the UI and demonstrate possible diagnostic outputs.
- They do not connect to OpenHuman's local memory files or a hosted TinyCortex workspace.
- Their displayed pass/fail states are scenario data, not measurements of a live pipeline.

## Summary Grounding Lab
- Checks are heuristic and primarily lexical.
- Entity patterns may miss names or flag valid expressions.
- Date and number checks identify candidates, not contradictions.
- Required-phrase checks are normalized exact matching; paraphrases can be flagged.
- Summary length is descriptive and is not itself a correctness signal.
- No heuristic flags does not prove factual accuracy, entailment, completeness, or safe use.
- Human review and source context remain necessary.

## Reports and persistence
- Report history is session-only and may not survive a restart or session expiration.
- JSON downloads are point-in-time exports.
- Grounding reports omit the source and summary text, but findings may contain candidate names or other text extracted from them. Review before sharing externally.
