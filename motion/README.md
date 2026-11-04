# Synthetic motion feasibility sample

An original, silent, 12-second vertical animation of a generic **brief → make → check** handoff. Cards activate in sequence, typography rises and reveals, progress bars fill, and curved paths draw between the steps. The visible labels say **AI-LED SYNTHETIC MOTION SAMPLE** and **NO CLIENT WORK**.

The Python source renders original procedural geometry and text with Pillow, then sends RGB frames to FFmpeg. It uses no external raster artwork, footage, music, voice or likeness.

The included MP4 is **1080 × 1920**, **24 fps**, **288 frames**, **12.000 seconds**, **H.264**, **yuv420p**, with **no audio stream**. The accompanying contact sheet contains eight frames decoded from the actual MP4.

Files: `create_motion_sample.py`, `brief-make-check-synthetic.mp4`, `contact-sheet.png`, `export-summary.json`, and the complete `LICENSE_DEJAVU.txt` font notice.

To reproduce with existing Python, Pillow, FFmpeg and ffprobe:

```sh
python3 create_motion_sample.py --font-dir /path/to/dejavu-fonts
```

`--font-dir` is required. That directory must contain unmodified `DejaVuSans.ttf`, `DejaVuSans-Bold.ttf` and their `LICENSE_DEJAVU` notice matching the included notice. The renderer writes outputs beside itself, replacing earlier exports. It downloads nothing, installs nothing and contacts no service. It removes only its own temporary log and decoded frames after creating the contact sheet.

The included portable export was tested with **Python 3.12.9**, **Pillow 12.2.0**, and **FFmpeg/ffprobe 6.1.1**. Automated checks confirmed exact stream specifications, 6,162 text-bound checks without failures, and six pixel-change comparisons across the encoded progression. An AI agent inspected the eight-timepoint contact sheet and full-size decoded frames at 5.0 and 11.5 seconds; no clipped or overlapping text was observed. This was selected-frame inspection, not continuous playback review or formal accessibility testing. The export summary records the measured execution timing as one-machine calibration only.

DejaVu Sans regular and bold are rasterized into the video; font binaries are not distributed here. Keep the included full font notice with redistributions. Its license applies to the fonts; no copyright exclusivity is claimed for the AI-generated source or artwork.

This is one synthetic technical example. It establishes no client history, paid delivery, professional reel assessment, sustained throughput or repeatable production capacity.
