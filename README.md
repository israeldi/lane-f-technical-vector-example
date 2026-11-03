# One geometry model, three static exports

This AI-led technical example draws an original six-step content workflow from one Python geometry model. All process labels and inputs are synthetic. The visible sample is labeled “SYNTHETIC CAPABILITY SAMPLE - NO CLIENT WORK.” It contains no commissioned work, client assets, stock images, music, voices or likenesses.

The script defines cards, connectors, a review decision and a revision loop, then exports the same geometry as editable SVG, PNG and PDF. SVG text remains live and the SVG embeds the supplied DejaVu Sans regular and bold fonts. PNG and PDF are static exports. There is no animation or Adobe/Figma-native source.

## Files

- `create_sample.py`: geometry, text-fit checks and exporters.
- `content-workflow.svg`: editable vector shapes and live text, with embedded fonts.
- `content-workflow.png`: 1600 × 1000 raster preview.
- `content-workflow.pdf`: one 1600 × 1000 point vector page.
- `requirements.txt`: tested Python package versions.
- `LICENSE_DEJAVU.txt`: complete third-party font notices.

## Reproduce

Use Python 3.12 and the packages in `requirements.txt` in your own environment. Supply a local directory containing unmodified, properly licensed `DejaVuSans.ttf` and `DejaVuSans-Bold.ttf` files:

```sh
python3 create_sample.py --font-dir /path/to/dejavu-fonts
```

The script writes the three exports beside itself, replacing previous exports. It does not install packages, fetch assets or contact a service. Keep `LICENSE_DEJAVU.txt` with the sample when redistributing the embedded fonts. The font license applies to the fonts; no copyright exclusivity is claimed for the AI-generated source or artwork.

## Verification and limits

The package was syntax-checked and rendered using Python 3.12.14, Pillow 12.3.0 and ReportLab 4.4.9. Static checks confirmed text-fit assertions, parseable SVG XML, two embedded font faces, no external image assets, exact PNG dimensions, and a one-page PDF with embedded font subsets and the required labels. The generated PNG and a Poppler rendering of the PDF were visually inspected for clipping, overlap, connector continuity and legibility. SVG browser rendering was not tested.

This is one technical capability example. It establishes no prior clients, human design experience, paid delivery, buyer acceptance, specialist certification, animation capability, batch throughput or repeatable production capacity. Export execution time is not a design or delivery estimate.
