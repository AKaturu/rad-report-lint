# Demo Media

The repository demo assets use a synthetic report scenario and deterministic lint output. They do not contain patient, institutional, or live clinical data.

## Files

- `docs/assets/demo.gif` - README animation
- `docs/assets/demo.mp4` - downloadable demo clip
- `docs/assets/demo-poster.png` - static preview frame

## Regenerate

```bash
python -m pip install -e ".[media]"
python scripts/generate_demo_media.py
```

The generator renders a stable final frame and duplicates it for the GIF/MP4 so the demo does not flicker on GitHub.
