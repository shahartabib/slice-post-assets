#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud-portable fill for Slice empty branded templates (all 1122x1402, 4:5).
Used by the slice-marketing-dept Cloud Routine (runs on a Linux sandbox, no Windows fonts,
no OneDrive). Templates live in ./templates, brand fonts in ./fonts, output goes to ./images.

Fonts: drop Archivo-Black.ttf + Archivo-SemiBold.ttf (Google Fonts, OFL) into ./fonts for the
closest match to the Segoe UI Black / Semibold brand look. If absent, falls back to DejaVu so
the routine still produces an image (lower fidelity) rather than crashing.

Import the fill_* functions from a weekly driver, or run this file to regenerate the samples.
Brand colors: white #FFF, grey (196,194,214), purple-white #ECE7FF, purple #7F4EFF.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, 'fonts')
TPL_DIR  = os.path.join(HERE, 'templates')
OUT_DIR  = os.path.join(HERE, 'images')
os.makedirs(OUT_DIR, exist_ok=True)

WHITE=(255,255,255); GREY=(196,194,214); PWHITE=(236,231,255); PUR=(127,78,255)

_LINUX_FALLBACK = {
    'black': ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'],
    'semi':  ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'],
}
def _font(candidates, kind, size):
    for n in candidates:
        p = os.path.join(FONT_DIR, n)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    for fb in _LINUX_FALLBACK[kind]:
        if os.path.exists(fb):
            return ImageFont.truetype(fb, size)
    return ImageFont.load_default()
def BL(s): return _font(['Archivo-Black.ttf', 'seguibl.ttf'], 'black', s)
def SB(s): return _font(['Archivo-SemiBold.ttf', 'seguisb.ttf'], 'semi', s)

def _tpl(name): return os.path.join(TPL_DIR, name)
def _out(name): return os.path.join(OUT_DIR, name)
def lines(d,x,y,arr,font,fill,step):
    for i,l in enumerate(arr): d.text((x,y+i*step),l,font=font,fill=fill)

# ---------------------------------------------------------------- DATAGRID  (6-cell 2x3)
DG_CELLS=[(84,417,True),(577,417,False),(84,745,False),(577,745,False),(84,1073,False),(577,1073,True)]
def fill_datagrid(out, title, stats, source='Source: TalentLMS, Docebo, eLearning Industry 2025', src='DataGrid.png'):
    # title=(line1,line2); stats=list of 6 (num,'label1|label2') in reading order C1..C6
    im=Image.open(_tpl(src)).convert('RGB'); d=ImageDraw.Draw(im)
    for (x0,y0,purple),(num,lbl) in zip(DG_CELLS,stats):
        d.text((x0+40,y0+44),num,font=BL(98),fill=WHITE)
        lines(d,x0+40,y0+162,lbl.split('|'),SB(31),PWHITE if purple else GREY,38)
    d.text((84,238),title[0],font=BL(62),fill=WHITE)
    d.text((84,306),title[1],font=BL(62),fill=PUR)
    d.text((577,1376),source,font=SB(20),fill=(150,148,170))
    p=_out(out); im.save(p); return p

# ---------------------------------------------------------------- CASE STUDY
def fill_casestudy(out, label, headline, subhead, stats, src='case study.png'):
    # headline=list of lines; stats=list of 3 (num,label)
    im=Image.open(_tpl(src)).convert('RGB'); d=ImageDraw.Draw(im)
    d.text((84,250),label,font=SB(26),fill=PUR)
    lines(d,84,296,headline,BL(70),WHITE,82)
    d.text((84,296+len(headline)*82+12),subhead,font=SB(30),fill=GREY)
    for (num,lbl),x in zip(stats,[84,430,776]):
        d.text((x,1030),num,font=BL(74),fill=WHITE); d.text((x,1122),lbl,font=SB(28),fill=GREY)
    p=_out(out); im.save(p); return p

# ---------------------------------------------------------------- TESTIMONIAL
def fill_testimonial(out, quote, author, stats, src='Testimonial.png'):
    im=Image.open(_tpl(src)).convert('RGB'); d=ImageDraw.Draw(im)
    lines(d,430,150,quote,BL(38),WHITE,52)
    d.text((430,150+len(quote)*52+8),author,font=SB(26),fill=GREY)
    for (num,lbl),x in zip(stats,[84,577]):
        d.text((x,1000),num,font=BL(72),fill=WHITE); d.text((x,1092),lbl,font=SB(28),fill=GREY)
    p=_out(out); im.save(p); return p

# ---------------------------------------------------------------- PHOTO OVERLAY / GRID (single headline)
def fill_headline(out, headline, subhead, hsize=72, src='Photo Overlay.png'):
    im=Image.open(_tpl(src)).convert('RGB'); d=ImageDraw.Draw(im)
    y0=1040 if len(headline)<=2 else 1010
    lines(d,84,y0,headline,BL(hsize),WHITE,hsize+12)
    d.text((84,y0+len(headline)*(hsize+12)+20),subhead,font=SB(30),fill=GREY)
    p=_out(out); im.save(p); return p

if __name__=='__main__':
    fill_datagrid('sample_datagrid.png',('The gap,','in numbers'),[
        ('89%','want training tailored|to their role'),('70%','would rather|learn online'),
        ('31%','find their current|system easy to use'),('35%','finish a course|without a nudge'),
        ('61%','of L&D managers|feel stuck'),('11%','can measure|training’s impact')])
    print('filled sample(s) into', OUT_DIR)
