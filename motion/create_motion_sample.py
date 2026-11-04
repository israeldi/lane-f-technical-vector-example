#!/usr/bin/env python3
"""Original silent procedural motion feasibility sample; no external artwork.
Run with the existing Python/Pillow and ffmpeg. All writes stay beside this file.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, math, platform, shutil, subprocess, time
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageStat, __version__ as pillow_version

ROOT = Path(__file__).resolve().parent
PARSER = argparse.ArgumentParser(description='Render one original 12-second synthetic motion sample.')
PARSER.add_argument('--font-dir', required=True, type=Path,
                    help='Directory containing DejaVuSans.ttf, DejaVuSans-Bold.ttf and LICENSE_DEJAVU.')
ARGS = PARSER.parse_args()
FONT_DIR = ARGS.font_dir.expanduser().resolve()
FONT_NAMES = {'regular': 'DejaVuSans.ttf', 'bold': 'DejaVuSans-Bold.ttf'}
FONT_PATHS = {key: str(FONT_DIR / name) for key, name in FONT_NAMES.items()}
LICENSE_SOURCE = FONT_DIR / 'LICENSE_DEJAVU'
LICENSE_REFERENCE = ROOT / 'LICENSE_DEJAVU.txt'
assert LICENSE_SOURCE.read_bytes() == LICENSE_REFERENCE.read_bytes(), 'Supplied font license differs from included notice'
assert 'Permission is hereby granted' in LICENSE_SOURCE.read_text()
for path in FONT_PATHS.values():
    assert Path(path).is_file(), 'A required DejaVu font is missing'
SCRATCH = ROOT / '_render_intermediates'
SCRATCH.mkdir(exist_ok=False)
W, H, FPS, SECONDS = 1080, 1920, 24, 12
COUNT = FPS * SECONDS
VIDEO = ROOT / 'brief-make-check-synthetic.mp4'
BG, WHITE, MUTED = '#0B1220', '#F2F5F7', '#A6B5CA'
COLORS = ['#AEBCFF', '#7EE4CB', '#FFBD98']
FONTS = {}
BOUNDS = {'drawn_text_instances': 0, 'canvas_checks': 0, 'region_checks': 0, 'failures': [], 'unique_full_labels': set()}

def font(size, bold=False):
    key = (size, bold)
    if key not in FONTS:
        FONTS[key] = ImageFont.truetype(FONT_PATHS['bold' if bold else 'regular'], size)
    return FONTS[key]

def clamp(v):
    return max(0.0, min(1.0, v))

def ease(v):
    v = clamp(v)
    return v * v * (3.0 - 2.0 * v)

def rgb(color):
    return tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))

def blend(a, b, weight):
    return tuple(round(x * (1 - weight) + y * weight) for x, y in zip(rgb(a), rgb(b)))

def label(draw, xy, value, size, fill=WHITE, bold=False, anchor=None, region=None):
    f = font(size, bold)
    bounds = draw.textbbox(xy, value, font=f, anchor=anchor)
    BOUNDS['drawn_text_instances'] += 1
    BOUNDS['canvas_checks'] += 1
    if not (0 <= bounds[0] <= bounds[2] <= W and 0 <= bounds[1] <= bounds[3] <= H):
        BOUNDS['failures'].append({'text': value, 'bounds': bounds, 'type': 'canvas'})
    if region:
        BOUNDS['region_checks'] += 1
        if not (region[0] <= bounds[0] <= bounds[2] <= region[2] and region[1] <= bounds[1] <= bounds[3] <= region[3]):
            BOUNDS['failures'].append({'text': value, 'bounds': bounds, 'region': region, 'type': 'region'})
    BOUNDS['unique_full_labels'].add(value)
    draw.text(xy, value, font=f, fill=fill, anchor=anchor)

# Code-created background: no raster source, image generator, stock asset, or photograph.
BACKGROUND = Image.new('RGB', (W, H), BG)
bd = ImageDraw.Draw(BACKGROUND)
for y in range(H):
    q = y / H
    bd.line((0, y, W, y), fill=blend('#101C31', '#080E19', q))
for x in range(88, W, 72):
    for y in range(500, 1530, 72):
        bd.ellipse((x, y, x + 2, y + 2), fill='#1C2B43')

STEPS = [
    {'title': 'BRIEF', 'body': 'Set the goal.', 'detail': 'Purpose / format / constraints', 'y': 540, 'start': .55, 'status': 'DEFINED'},
    {'title': 'MAKE', 'body': 'Build the idea.', 'detail': 'Geometry / sequence / timing', 'y': 870, 'start': 4.05, 'status': 'CREATED'},
    {'title': 'CHECK', 'body': 'Inspect the result.', 'detail': 'Readability / motion / export', 'y': 1200, 'start': 7.55, 'status': 'CHECKED'},
]

def connector(draw, y, start, color, t):
    # Original curved path, drawn progressively; moving dot exposes handoff direction.
    points = [(540 + 50 * math.sin(math.pi * n / 80), y + n) for n in range(81)]
    draw.line(points, fill='#27384F', width=5, joint='curve')
    progress = ease((t - start) / 1.2)
    upto = round(progress * 80)
    if upto > 0:
        draw.line(points[:upto + 1], fill=color, width=7, joint='curve')
        px, py = points[upto]
        draw.ellipse((px - 10, py - 10, px + 10, py + 10), fill=color)
    if progress > .97:
        draw.polygon([(529, y + 68), (551, y + 68), (540, y + 81)], fill=color)

def icon(draw, cx, cy, stage, color, progress):
    # All icons are original geometric instructions, not stock icon paths.
    draw.rounded_rectangle((cx - 37, cy - 37, cx + 37, cy + 37), radius=18, fill='#17273A', outline=color, width=2)
    if stage == 0:
        for j, length in enumerate([34, 26, 18]):
            draw.rounded_rectangle((cx - 17, cy - 16 + j * 14, cx - 17 + length, cy - 12 + j * 14), radius=2, fill=color)
    elif stage == 1:
        rotation = (1 - progress) * .75
        for j in range(4):
            a = math.pi / 2 * j + rotation
            px, py = cx + 17 * math.cos(a), cy + 17 * math.sin(a)
            draw.rounded_rectangle((px - 8, py - 8, px + 8, py + 8), radius=3, fill=color)
    else:
        path = [(cx - 17, cy + 1), (cx - 4, cy + 14), (cx + 20, cy - 15)]
        draw.line(path, fill=color, width=7, joint='curve')


def render(t):
    im = BACKGROUND.copy()
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((88, 100, 992, 159), radius=18, fill='#1C2A42', outline='#34455F', width=1)
    label(d, (540, 129), 'AI-LED SYNTHETIC MOTION SAMPLE', 28, bold=True, anchor='mm', region=(100, 108, 980, 151))
    label(d, (88, 211), 'Three steps.', 76, bold=True, region=(88, 200, 995, 310))
    label(d, (88, 308), 'One clear handoff.', 76, bold=True, region=(88, 300, 1010, 415))
    label(d, (90, 438), 'From a clear brief to a checked result.', 32, fill=MUTED, region=(88, 430, 1000, 489))
    connector(d, 790, 2.95, COLORS[0], t)
    connector(d, 1120, 6.45, COLORS[1], t)
    for i, s in enumerate(STEPS):
        active = ease((t - s['start']) / .75)
        settled = ease((t - s['start'] - 1.45) / .7)
        color = blend('#50617B', COLORS[i], active)
        y = s['y']
        d.rounded_rectangle((104, y + 10, 976, y + 260), radius=30, fill='#070D17')
        d.rounded_rectangle((104, y, 976, y + 250), radius=30, fill=blend('#111D2D', '#1A2D3F', active), outline=color, width=2)
        d.rounded_rectangle((104, y + 30, 111, y + 220), radius=3, fill=color)
        d.rounded_rectangle((136, y + 35, 212, y + 111), radius=21, fill=color)
        label(d, (174, y + 74), f'{i + 1:02d}', 30, fill='#0B1220', bold=True, anchor='mm', region=(140, y + 38, 209, y + 108))
        # Card heading and body rise into place; body reveals character by character.
        offset = round((1 - active) * 18)
        label(d, (246, y + 29 + offset), s['title'], 44, fill=blend('#7E90AA', WHITE, active), bold=True, region=(235, y + 25, 805, y + 112))
        reveal = clamp((t - s['start'] - .15) / .9)
        body = s['body'][:round(len(s['body']) * reveal)]
        if body:
            label(d, (246, y + 99 + offset), body, 39, fill=WHITE, bold=True, region=(235, y + 97, 902, y + 176))
        label(d, (246, y + 176), s['detail'], 25, fill=blend('#657990', MUTED, active), region=(235, y + 175, 912, y + 218))
        icon(d, 892, y + 71, i, color, active)
        d.rounded_rectangle((246, y + 224, 909, y + 230), radius=3, fill='#314359')
        fill_width = round(663 * clamp((t - s['start']) / 2.1))
        if fill_width > 3:
            d.rounded_rectangle((246, y + 224, 246 + fill_width, y + 230), radius=3, fill=color)
        if settled > .99:
            label(d, (821, y + 130), s['status'], 16, fill=color, bold=True, region=(800, y + 125, 965, y + 165))
    completed = sum(t >= s['start'] + 2.1 for s in STEPS)
    d.rounded_rectangle((304, 1530, 776, 1592), radius=31, fill='#17283A', outline='#35516A', width=1)
    status = f'{completed} / 3 STEPS COMPLETE' if t < 10.2 else 'HANDOFF COMPLETE'
    label(d, (540, 1562), status, 24, fill=COLORS[1] if completed == 3 else MUTED, bold=True, anchor='mm', region=(315, 1538, 765, 1586))
    label(d, (540, 1670), 'NO CLIENT WORK', 35, fill=WHITE, bold=True, anchor='mm', region=(100, 1630, 980, 1710))
    label(d, (540, 1725), 'Original procedural animation / silent', 25, fill=MUTED, anchor='mm', region=(100, 1700, 980, 1755))
    d.rounded_rectangle((104, 1806, 976, 1812), radius=3, fill='#314359')
    timeline = round(872 * clamp(t / (SECONDS - 1 / FPS)))
    if timeline > 2:
        d.rounded_rectangle((104, 1806, 104 + timeline, 1812), radius=3, fill=COLORS[1])
    label(d, (104, 1834), '12-SECOND FEASIBILITY SAMPLE', 19, fill='#8B9CB4', region=(100, 1825, 880, 1880))
    label(d, (976, 1846), f'{t:04.1f}s', 19, fill=MUTED, anchor='rm', region=(880, 1825, 985, 1880))
    return im

started = time.perf_counter()
ffmpeg = shutil.which('ffmpeg')
ffprobe = shutil.which('ffprobe')
assert ffmpeg and ffprobe
command = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', 'pipe:0', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '19', '-threads', '4', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-metadata', 'title=AI-led synthetic motion sample - no client work', str(VIDEO)]
render_seconds = 0.0
feed_seconds = 0.0
with (SCRATCH / 'ffmpeg.log').open('wb') as log:
    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=log)
    for frame in range(COUNT):
        t0 = time.perf_counter()
        image = render(frame / FPS)
        render_seconds += time.perf_counter() - t0
        t0 = time.perf_counter()
        proc.stdin.write(image.tobytes())
        feed_seconds += time.perf_counter() - t0
    proc.stdin.close()
    result = proc.wait()
    assert result == 0, (SCRATCH / 'ffmpeg.log').read_text()
export_seconds = time.perf_counter() - started
assert not BOUNDS['failures'], BOUNDS['failures'][:10]
probe = json.loads(subprocess.check_output([ffprobe, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(VIDEO)]))
vs = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
assert len(vs) == 1
v = vs[0]
assert (v['width'], v['height']) == (W, H)
assert v['codec_name'] == 'h264' and v['pix_fmt'] == 'yuv420p'
assert v['r_frame_rate'] == '24/1' and v['avg_frame_rate'] == '24/1'
assert int(v['nb_frames']) == COUNT and abs(float(v['duration']) - SECONDS) < .001
assert not any(stream['codec_type'] == 'audio' for stream in probe['streams'])

# Inspect the actual encoded export at fixed points, not only source frames.
TIMES = [0.0, 1.5, 3.5, 5.0, 6.75, 8.25, 9.5, 11.5]
extracted = []
for n, ts in enumerate(TIMES):
    path = SCRATCH / f'encoded-frame-{n:02d}.png'
    subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-y', '-ss', str(ts), '-i', str(VIDEO), '-frames:v', '1', str(path)], check=True)
    extracted.append(Image.open(path).convert('RGB'))
contact = Image.new('RGB', (1080, 1036), '#0B1220')
cd = ImageDraw.Draw(contact)
for n, (ts, frame) in enumerate(zip(TIMES, extracted)):
    x, y = (n % 4) * 270, (n // 4) * 518
    contact.paste(frame.resize((270, 480), Image.Resampling.LANCZOS), (x, y + 34))
    cd.text((x + 12, y + 7), f'{ts:04.2f} s', font=font(17, True), fill=WHITE)
contact.save(ROOT / 'contact-sheet.png')

regions = {
    'brief_card_typography_progress_0_to_1_5': (0, 1, (240, 560, 915, 780)),
    'first_path_progress_1_5_to_3_5': (1, 2, (510, 788, 610, 871)),
    'make_card_typography_progress_3_5_to_5': (2, 3, (240, 890, 915, 1110)),
    'second_path_progress_5_to_6_75': (3, 4, (510, 1118, 610, 1201)),
    'check_card_typography_progress_6_75_to_8_25': (4, 5, (240, 1220, 915, 1440)),
    'completion_progress_9_5_to_11_5': (6, 7, (304, 1530, 776, 1592)),
}
encoded_cue_checks = {}
for name, (a, b, box) in regions.items():
    diff = ImageChops.difference(extracted[a].crop(box), extracted[b].crop(box))
    mean = sum(ImageStat.Stat(diff).mean) / 3
    encoded_cue_checks[name] = {'mean_absolute_rgb_difference': round(mean, 4), 'visible_pixel_change': mean > 1.0}
    assert mean > 1, name

# Only the temporary files created by this script are removed.
expected = {'ffmpeg.log', *[f'encoded-frame-{n:02d}.png' for n in range(len(TIMES))]}
assert {p.name for p in SCRATCH.iterdir()} == expected
for name in sorted(expected):
    (SCRATCH / name).unlink()
SCRATCH.rmdir()

file_info = {}
for name in ['create_motion_sample.py', VIDEO.name, 'contact-sheet.png', 'LICENSE_DEJAVU.txt']:
    path = ROOT / name
    file_info[name] = {'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
summary = {
    'sample': 'Original generic brief -> make -> check motion handoff',
    'status': 'EXPORT_AND_AUTOMATED_CHECKS_PASS; AGENT_SELECTED_FRAME_REVIEW_PENDING',
    'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    'visible_disclosure': ['AI-LED SYNTHETIC MOTION SAMPLE', 'NO CLIENT WORK'],
    'source': 'create_motion_sample.py',
    'output': VIDEO.name,
    'tools': {'python': platform.python_version(), 'pillow': pillow_version,
              'ffmpeg': subprocess.check_output([ffmpeg, '-version'], text=True).splitlines()[0]},
    'specification': {'width': W, 'height': H, 'duration_seconds': SECONDS,
                      'frames': COUNT, 'frames_per_second': FPS, 'codec': v['codec_name'],
                      'pixel_format': v['pix_fmt'], 'audio_stream_count': 0},
    'observed_calibration': {'render_and_export_wall_seconds': round(export_seconds, 3),
                             'pillow_render_wall_seconds': round(render_seconds, 3),
                             'raw_frame_feed_wall_seconds': round(feed_seconds, 3),
                             'scope': 'One render/export on one machine; render and encoder overlap. Excludes planning, authoring and review. Timing is a calibration observation only.'},
    'rights': {'artwork': 'Original procedural geometry, paths, geometric icons and labels authored in this script; no external raster artwork.',
               'font_files': FONT_NAMES,
               'font_sha256': {key: hashlib.sha256(Path(path).read_bytes()).hexdigest() for key, path in FONT_PATHS.items()},
               'font_license_copy': 'LICENSE_DEJAVU.txt',
               'font_license_matches_supplied_font_directory': True,
               'font_license': 'Included unmodified notice permits use and distribution subject to its conditions. Unmodified fonts are rasterized into the video; font binaries are not redistributed.',
               'music_voice_likeness_footage_external_artwork': 'None'},
    'checks': {'ffprobe': {'width': v['width'], 'height': v['height'],
                           'codec_name': v['codec_name'], 'pix_fmt': v['pix_fmt'],
                           'r_frame_rate': v['r_frame_rate'], 'avg_frame_rate': v['avg_frame_rate'],
                           'duration': v['duration'], 'nb_frames': v['nb_frames'],
                           'format_duration': probe['format']['duration'], 'audio_stream_count': 0},
               'text_bounds': {'drawn_text_instances': BOUNDS['drawn_text_instances'],
                               'canvas_checks': BOUNDS['canvas_checks'],
                               'region_checks': BOUNDS['region_checks'], 'failures': BOUNDS['failures']},
               'encoded_animation_cue_checks': encoded_cue_checks,
               'selected_actual_export_frame_times_seconds': TIMES,
               'agent_selected_frame_review': {'status': 'PENDING',
                                                'scope': 'Automated checks do not perform visual assessment. Review the decoded contact sheet and selected full-size decoded frames separately.'}},
    'limitations': ['One original silent synthetic feasibility example.',
                    'Selected-frame and technical checks do not establish continuous-playback review, professional animation quality or accessibility conformance.',
                    'No voice, music, footage, likeness, character animation or Adobe-native source included.'],
    'files': file_info,
    'temporary_files': 'Only the temporary log and eight decoded PNG frames created by this render were removed after assembling the contact sheet.'
}
(ROOT / 'export-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({'video': VIDEO.name, 'render_and_export_wall_seconds': round(export_seconds, 3),
                  'text_bounds_failures': len(BOUNDS['failures']), 'frames': COUNT,
                  'contact_sheet': 'contact-sheet.png', 'summary': 'export-summary.json'}, indent=2))
