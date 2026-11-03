#!/usr/bin/env python3
"""Original synthetic six-step content workflow, exported from one geometry model."""
from pathlib import Path
import argparse, base64, html, json, math
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--font-dir', type=Path, required=True,
                    help='Directory containing licensed DejaVuSans.ttf and DejaVuSans-Bold.ttf')
args = parser.parse_args()
ROOT = Path(__file__).resolve().parent
W, H = 1600, 1000
FONT_ROOT = args.font_dir.expanduser().resolve()
FONTS = {'regular': FONT_ROOT/'DejaVuSans.ttf', 'bold': FONT_ROOT/'DejaVuSans-Bold.ttf'}
LICENSE = ROOT/'LICENSE_DEJAVU.txt'
assert all(p.exists() for p in [*FONTS.values(), LICENSE])
license_text = LICENSE.read_text()
assert 'publish, distribute, and/or sell copies' in license_text
ROOT.mkdir(parents=True, exist_ok=True)
for weight, path in FONTS.items():
    pdfmetrics.registerFont(TTFont('Probe-'+weight, str(path)))

C = {'bg':'#F4F3ED','ink':'#193B38','muted':'#536B66','line':'#C7D3CB','teal':'#246E61','mint':'#E6F0E9','white':'#FFFFFF','amber':'#A76527','paleamber':'#FBEDDD'}
ops, text_checks = [], []
def rect(x,y,w,h,fill,stroke=None,r=0,sw=1):
    ops.append(('rect',dict(x=x,y=y,w=w,h=h,fill=fill,stroke=stroke,r=r,sw=sw)))
def polygon(points,fill,stroke=None,sw=1):
    ops.append(('polygon',dict(points=points,fill=fill,stroke=stroke,sw=sw)))
def line(points,stroke,sw=4,arrow=False):
    ops.append(('line',dict(points=points,stroke=stroke,sw=sw)))
    if arrow:
        x,y=points[-1]; px,py=points[-2];a=math.atan2(y-py,x-px)
        pts=[(x,y),(x-15*math.cos(a)+7*math.sin(a),y-15*math.sin(a)-7*math.cos(a)),(x-15*math.cos(a)-7*math.sin(a),y-15*math.sin(a)+7*math.cos(a))]
        polygon(pts,stroke)
def text(x,y,value,size=22,fill=None,weight='regular',anchor='start',max_width=None):
    # Coordinates use alphabetic baselines, shared by SVG, Pillow, and PDF.
    font=ImageFont.truetype(str(FONTS[weight]),size)
    width=font.getlength(value)
    left=x if anchor=='start' else x-width/2 if anchor=='middle' else x-width
    if max_width is not None:
        assert width <= max_width, (value,width,max_width)
    assert left >= 0 and left+width <= W and 0 <= y-size and y <= H, value
    text_checks.append({'text':value,'width_px':round(width,2),'max_width_px':max_width,'fits':True})
    ops.append(('text',dict(x=x,y=y,value=value,size=size,fill=fill or C['ink'],weight=weight,anchor=anchor)))
def card(x,y,step,kicker,title,body,accent=False):
    rect(x,y,350,150,C['mint'] if accent else C['white'],C['teal'] if accent else C['line'],18,2 if accent else 1)
    rect(x+24,y+22,31,25,C['teal'],None,7)
    text(x+39.5,y+39,step,13,C['white'],'bold','middle')
    text(x+68,y+39,kicker,14,C['muted'],'bold',max_width=258)
    text(x+24,y+80,title,26,weight='bold',max_width=302)
    for i,s in enumerate(body):text(x+24,y+111+i*25,s,20,C['muted'],max_width=302)

rect(0,0,W,H,C['bg'])
rect(80,65,1440,1,C['line'])
text(80,105,'SYNTHETIC CAPABILITY SAMPLE - NO CLIENT WORK',18,C['teal'],'bold',max_width=1440)
text(80,181,'From request to approved handoff',56,weight='bold',max_width=1440)
text(80,224,'A six-step production workflow with one clear revision loop.',24,C['muted'],max_width=1440)

# Main path: clockwise from request to export checks, then left through review.
line([(430,355),(625,355)],C['teal'],4,True)
line([(975,355),(1170,355)],C['teal'],4,True)
line([(1345,430),(1345,610)],C['teal'],4,True)
line([(1170,685),(920,685)],C['teal'],4,True)
line([(680,685),(430,685)],C['teal'],4,True)
# Review loops to a separate input port on the build card; no path crossings.
line([(800,585),(800,505),(1250,505),(1250,430)],C['amber'],4,True)
rect(846,480,286,48,C['paleamber'],None,24)
text(989,511,'Revision requested',19,C['amber'],'bold','middle')
text(533,334,'Clarified brief',17,C['muted'],anchor='middle')
text(1073,334,'Ready to build',17,C['muted'],anchor='middle')
text(1364,527,'Export',17,C['muted'])
rect(985,653,132,29,C['bg'],None,6)
text(1051,674,'For review',17,C['muted'],anchor='middle')
rect(493,653,124,29,C['bg'],None,6)
text(555,674,'Approved',17,C['teal'],'bold','middle')

card(80,280,'01','INPUT','Request received',['Goal, audience and channels'])
card(625,280,'02','SCOPE','Brief + asset rights',['Scope, supplied inputs','and commercial permissions'])
card(1170,280,'03','PRODUCTION','Build assets',['Original artwork in a','controlled source file'])
card(1170,610,'04','QUALITY CHECK','Verify exports',['Check size, copy and format','before client review'])
polygon([(800,585),(920,685),(800,785),(680,685)],C['white'],C['teal'],2)
text(800,653,'05 / DECISION',14,C['muted'],'bold','middle')
text(800,689,'Client review',24,weight='bold',anchor='middle')
text(800,722,'Approve?',19,C['muted'],anchor='middle')
card(80,610,'06','DELIVERY','Approved handoff',['Masters, editable source','and a file manifest'],True)

rect(80,864,1440,78,C['white'],C['line'],14)
text(104,894,'REPEATABLE STRUCTURE',14,C['teal'],'bold')
text(104,923,'One brief. One review loop. One controlled asset set.',21,C['ink'])
text(1495,914,'Original geometry / synthetic inputs',16,C['muted'],anchor='end')
text(80,973,'Illustrative process only. No client assets, commissioned work or commercial acceptance implied.',16,C['muted'])

# Portable SVG retains live text and embeds the two unmodified licensed fonts.
svg=['<?xml version="1.0" encoding="UTF-8"?>',f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
     '<title id="title">Synthetic content production workflow</title>',
     '<desc id="desc">Request received, brief and asset rights, build assets, verify exports, client review, and approved handoff. A revision-request loop returns from review to production. Synthetic capability sample, no client work.</desc>', '<defs><style>']
for weight,path in FONTS.items():
    data=base64.b64encode(path.read_bytes()).decode()
    svg.append("@font-face{font-family:'ProbeDejaVu';font-style:normal;font-weight:"+('700' if weight=='bold' else '400')+";src:url(data:font/ttf;base64,"+data+") format('truetype');}")
svg.append('</style></defs>')
for kind,o in ops:
    if kind=='rect':svg.append(f'<rect x="{o["x"]}" y="{o["y"]}" width="{o["w"]}" height="{o["h"]}" rx="{o["r"]}" fill="{o["fill"]}" stroke="{o["stroke"] or "none"}" stroke-width="{o["sw"]}"/>')
    elif kind=='polygon':svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in o['points'])+f'" fill="{o["fill"]}" stroke="{o["stroke"] or "none"}" stroke-width="{o["sw"]}"/>')
    elif kind=='line':svg.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in o['points'])+f'" fill="none" stroke="{o["stroke"]}" stroke-width="{o["sw"]}" stroke-linecap="round" stroke-linejoin="round"/>')
    else:svg.append(f'<text x="{o["x"]}" y="{o["y"]}" font-family="ProbeDejaVu" font-size="{o["size"]}" font-weight="{700 if o["weight"]=="bold" else 400}" text-anchor="{o["anchor"]}" fill="{o["fill"]}">{html.escape(o["value"])}</text>')
svg.append('</svg>')
(ROOT/'content-workflow.svg').write_text('\n'.join(svg))

# PNG and PDF export the identical geometry without an external renderer.
im=Image.new('RGB',(W,H),C['bg']);draw=ImageDraw.Draw(im)
pdf=canvas.Canvas(str(ROOT/'content-workflow.pdf'),pagesize=(W,H),pageCompression=1)
pdf.setTitle('Synthetic content production workflow - no client work')
pdf.setAuthor('AI-led synthetic example')
pdf.setCreator('AI-led synthetic example')
pdf.setSubject('Original synthetic workflow; no client work or commercial acceptance')
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
for kind,o in ops:
    if kind=='text':
        f=ImageFont.truetype(str(FONTS[o['weight']]),o['size'])
        a={'start':'ls','middle':'ms','end':'rs'}[o['anchor']]
        draw.text((o['x'],o['y']),o['value'],font=f,fill=o['fill'],anchor=a)
        pdf.setFillColorRGB(*rgb(o['fill']));pdf.setFont('Probe-'+o['weight'],o['size'])
        {'start':pdf.drawString,'middle':pdf.drawCentredString,'end':pdf.drawRightString}[o['anchor']](o['x'],H-o['y'],o['value'])
    elif kind=='rect':
        draw.rounded_rectangle((o['x'],o['y'],o['x']+o['w'],o['y']+o['h']),radius=o['r'],fill=o['fill'],outline=o['stroke'],width=o['sw'])
        pdf.setFillColorRGB(*rgb(o['fill']));pdf.setLineWidth(o['sw'])
        if o['stroke']:pdf.setStrokeColorRGB(*rgb(o['stroke']))
        pdf.roundRect(o['x'],H-o['y']-o['h'],o['w'],o['h'],o['r'],fill=1,stroke=int(bool(o['stroke'])))
    elif kind=='polygon':
        draw.polygon(o['points'],fill=o['fill'],outline=o['stroke'],width=o['sw'])
        p=pdf.beginPath();p.moveTo(o['points'][0][0],H-o['points'][0][1])
        for x,y in o['points'][1:]:p.lineTo(x,H-y)
        p.close();pdf.setFillColorRGB(*rgb(o['fill']));pdf.setLineWidth(o['sw'])
        if o['stroke']:pdf.setStrokeColorRGB(*rgb(o['stroke']))
        pdf.drawPath(p,fill=1,stroke=int(bool(o['stroke'])))
    else:
        draw.line(o['points'],fill=o['stroke'],width=o['sw'],joint='curve')
        p=pdf.beginPath();p.moveTo(o['points'][0][0],H-o['points'][0][1])
        for x,y in o['points'][1:]:p.lineTo(x,H-y)
        pdf.setStrokeColorRGB(*rgb(o['stroke']));pdf.setLineWidth(o['sw']);pdf.setLineJoin(1);pdf.setLineCap(1);pdf.drawPath(p)
im.save(ROOT/'content-workflow.png',optimize=True)
pdf.showPage();pdf.save()
print(json.dumps({'status': 'generated; inspect outputs before use',
                  'dimensions': [W, H],
                  'files': ['content-workflow.svg', 'content-workflow.png', 'content-workflow.pdf']}))
