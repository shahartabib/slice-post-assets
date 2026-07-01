# -*- coding: utf-8 -*-
"""Generate B & C AI abstracts, compose all 3 posts in the locked style (bright gradient +
screen-blended constellation + grid + accent-above-label + CLEAN, no thread). Show 3-up."""
import os,base64
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display
from openai import OpenAI

KEYFILE="C:/Users/Shahar Tabib/OneDrive - Sliceknowledge.com/Slice/שיווק סלייס/כלי שיווק/Open Ai API.txt"
POSTS="C:/Users/Shahar Tabib/OneDrive - Sliceknowledge.com/Slice/תוכנית עסקית/Pitch Deck/Strategy 2026/קווים עיצוביים/posts"
SD="C:/Users/SHAHAR~1/AppData/Local/Temp/claude/C--Users-Shahar-Tabib-OneDrive---Sliceknowledge-com-Slice--------------Pitch-Deck-Strategy-2026/80bf7f65-50df-4b6e-ba63-877930a8ee8f/scratchpad"
WHITE=(255,255,255); FADED=(120,96,196); LAV=(196,182,255); PUR=(127,78,255)
LEFT=84; RIGHT=1038; RY0,RY1=150,905
BLK="C:/Windows/Fonts/seguibl.ttf"; ARBD="C:/Windows/Fonts/arialbd.ttf"
base=Image.open(f"{POSTS}/Photo Overlay.png").convert("RGB"); W,H=base.size
bt=np.asarray(base).astype(float); YY,XX=np.mgrid[0:H,0:W].astype(float)
client=OpenAI(api_key=open(KEYFILE,encoding="utf-8-sig").read().strip())

def gen(prompt,out):
    if os.path.exists(out): print("cached",out); return out
    r=client.images.generate(model="gpt-image-1",prompt=prompt,size="1536x1024",quality="medium",n=1)
    open(out,"wb").write(base64.b64decode(r.data[0].b64_json)); print("generated",out); return out

PB=("Editorial abstract background for a premium enterprise tech brand. Pure black canvas. On the "
    "RIGHT, a large dense luminous cluster of many small glowing violet-white nodes, a bright body of "
    "collective knowledge. On the far LEFT, a single small isolated glowing node alone in vast empty "
    "black space. A very wide dark empty gap separates them. Minimalist, lots of negative space, soft "
    "bokeh glow, fine grain, violet #7F4EFF and white points on pure black. NO text, no letters, no "
    "people, no faces, not a stock photo. Cinematic, restrained, abstract data-constellation.")
PC=("Editorial abstract background for a premium enterprise tech brand. Pure black canvas. Three or four "
    "SEPARATE distinct glowing clusters of violet nodes, each a self-contained group, spaced apart from "
    "one another like different categories. Set clearly apart from all of them, a single notably brighter "
    "and larger lone glowing node stands alone. Minimalist, lots of negative space, soft bokeh glow, fine "
    "grain, violet #7F4EFF and white on pure black. NO text, no letters, no people, not a stock photo. "
    "Cinematic, restrained, abstract.")
rawB=gen(PB,f"{SD}/ai_B_raw.png"); rawC=gen(PC,f"{SD}/ai_C_raw.png")
rawA=f"{SD}/ai_A_raw.png"

def crop_fill(img,w,h):
    iw,ih=img.size; t=w/h; s=iw/ih
    if s>t: nw=int(ih*t); x=(iw-nw)//2; img=img.crop((x,0,x+nw,ih))
    else:   nh=int(iw/t); y=(ih-nh)//2; img=img.crop((0,y,iw,y+nh))
    return img.resize((w,h),Image.LANCZOS)

# locate baked underline once
ys,xs=np.mgrid[0:H,0:W]; regm=(ys>1050)&(ys<1250)&(xs<360)
R,G,B=bt[...,0],bt[...,1],bt[...,2]; m=regm&(B>120)&(R>90)&(R>G+25); yy2,xx2=np.where(m)
UX0,UX1,UY0,UY1=xx2.min(),xx2.max(),yy2.min(),yy2.max(); UW,UH=UX1-UX0+1,UY1-UY0+1
STEP=93.5

def compose(raw,lang,label,punch):
    ai=np.clip(np.asarray(crop_fill(Image.open(raw).convert("RGB"),W,RY1-RY0)).astype(float)*1.12,0,255)
    g=bt[RY0:RY1].copy(); screen=255-(255-g)*(255-ai)/255.0
    arr=bt.copy(); arr[RY0:RY1]=screen
    v=np.clip((YY-940)/(H-940),0,1)**1.5; arr=arr*(1-v[...,None]*0.5)
    img=Image.fromarray(np.clip(arr,0,255).astype(np.uint8),"RGB")
    dx=int(round(2*STEP)); pad=8; box=(UX0-pad,UY0-pad,UX1+pad,UY1+pad)
    img.paste(img.crop((box[0]+dx,box[1],box[2]+dx,box[3])),(box[0],box[1]))
    d=ImageDraw.Draw(img,"RGBA")
    def w_of(t,f): b=d.textbbox((0,0),t,font=f); return b[2]-b[0]
    lf=ImageFont.truetype(ARBD if lang=="he" else BLK,27 if lang=="he" else 26)
    pf=ImageFont.truetype(ARBD if lang=="he" else BLK,84)
    pstep=100; top=1300-pstep*len(punch); label_y=top-58; ay=label_y-30
    if lang=="he":
        ImageDraw.Draw(img).rounded_rectangle([RIGHT-UW,ay,RIGHT,ay+UH],radius=UH//2,fill=PUR)
        vis=get_display(label); d.text((RIGHT-w_of(vis,lf),label_y),vis,font=lf,fill=LAV)
        for i,(t,c) in enumerate(punch):
            vis=get_display(t); d.text((RIGHT-w_of(vis,pf),top+i*pstep),vis,font=pf,fill=c)
    else:
        ImageDraw.Draw(img).rounded_rectangle([LEFT,ay,LEFT+UW,ay+UH],radius=UH//2,fill=PUR)
        d.text((LEFT,label_y),label,font=lf,fill=LAV)
        for i,(t,c) in enumerate(punch):
            d.text((LEFT,top+i*pstep),t,font=pf,fill=c)
    return img

A=compose(rawA,"he","סלייס  /  תצפיות מהשטח",[("הרגע שבו",WHITE),("הנציג לבד.",FADED)])
Bimg=compose(rawB,"en","SLICEKNOWLEDGE  /  FIELD NOTES",[("Knowledge isn't",WHITE),("your problem.",WHITE),("Distance is.",FADED)])
Cimg=compose(rawC,"en","SLICEKNOWLEDGE  /  FIELD NOTES",[("We argue about",WHITE),("categories.",WHITE),("Buyers don't.",FADED)])
for nm,im in [("050726FB",A),("070726LI",Bimg),("090726LI",Cimg)]:
    im.save(f"{SD}/final_{nm}.png")

pw=384; ph=int(pw*H/W); cap=74; mar=34; gap=34
CW=mar*2+pw*3+gap*2; CH=mar+cap+ph+mar
cv=Image.new("RGB",(CW,CH),(17,15,28)); dd=ImageDraw.Draw(cv)
cf=ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf",25)
titles=["A · FB — the rep, alone","B · LI — Distance is","C · LI — Buyers don't care"]
for i,(t,im) in enumerate(zip(titles,[A,Bimg,Cimg])):
    x=mar+i*(pw+gap); cv.paste(im.resize((pw,ph),Image.LANCZOS),(x,mar+cap)); dd.text((x,mar+20),t,font=cf,fill=(236,231,255))
cv.save(f"{SD}/final_three.png"); print("saved 3-up")
