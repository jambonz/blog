# Vendor support charts

Draws `stt-vendor-matrix.png` and `tts-vendor-matrix.png` for the
[bring-your-own-everything](../../src/content/blog/bring-your-own-everything-voice-ai/) post.

To update: edit the vendor lists in `data.py`, then run

```bash
cd scripts/vendor-charts
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python chart.py
```

The PNGs are written into the post folder (pass a directory to write elsewhere).
Keep the counts in the post's tables in step with `data.py`.
