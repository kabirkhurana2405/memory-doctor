# Screenshot Guide

Use real screenshots from your running Memory Doctor app. Do not use mockups or synthetic images as though they were product screenshots.

## Capture
1. Run the app locally.
2. Use the synthetic grounding example and non-sensitive demo inputs.
3. Maximize the browser and keep the interface in its normal dark theme.
4. Capture with **Win + Shift + S** on Windows.
5. Save PNG files in `docs/images/` using the filenames below.
6. Make sure no API keys, personal data, local file paths, tokens, or unrelated desktop content are visible.

## Recommended screenshots

| Filename | Page | What to show |
|---|---|---|
| `overview.png` | Overview | Sidebar, title, and all tool cards |
| `sdk-contract-checker.png` | SDK Contract Checker | Loaded spec, source mode, detected routes and comparison results |
| `memory-diagnostics.png` | Memory Diagnostics | Successful health response and the clearly labelled memory access outcome; keep the key field empty or blurred |
| `summary-grounding-lab.png` | Summary Grounding Lab | Synthetic source and summary, charts, and findings |

For the SDK screenshot, use a small example OpenAPI spec and safe source file if the installed SDK output is too large or exposes local paths.

## Add screenshots to the README
Once the files exist, add this Markdown to the README where you want the screenshot gallery:

```markdown
## Screenshots

![Overview](docs/images/overview.png)
![SDK Contract Checker](docs/images/sdk-contract-checker.png)
![Memory Diagnostics](docs/images/memory-diagnostics.png)
![Summary Grounding Lab](docs/images/summary-grounding-lab.png)
```

Only include images that you have actually captured. If you publish one screenshot first, include only that image until the others are ready.
