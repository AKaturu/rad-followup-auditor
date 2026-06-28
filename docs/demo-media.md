# Demo Media

The README demo media is generated from a real CLI demo run against synthetic reports.

```bash
python -m pip install -e ".[media]"
python scripts/generate_demo_media.py
```

Generated assets:

- `docs/assets/demo-poster.png`
- `docs/assets/demo.gif`
- `docs/assets/demo.mp4`

The generated reports are synthetic and intended for demonstration. Real deployments should use de-identified local report CSVs.
