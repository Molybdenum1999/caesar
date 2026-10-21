import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
SRC='/home/user/caesar/';OUT=SRC+'game/assets/'
p0=np.array(Image.open(SRC+'progress0:3.png').convert('RGBA'))
p1=np.array(Image.open(SRC+'13.png').convert('RGBA'))
dk=lambda a:(a[...,3]>100)&(a[...,:3].sum(-1)<330)
X0,Y0,X1,Y1=1100,1030,1720,1160
def crop(a): return a[Y0:Y1,X0:X1].copy()
c0,c1=crop(p0),crop(p1)
hatch=dk(c1)&~ndimage.binary_dilation(dk(c0),iterations=3)
hatch[:, 150:]=False
hy,hx=np.where(hatch)
def boxinterior(c,xa,xb):
    m=dk(c).copy(); m[:,:xa]=False; m[:,xb:]=False
    f=ndimage.binary_fill_holes(ndimage.binary_closing(m,iterations=2))
    return ndimage.binary_erosion(f&~m,iterations=2)
def addhatch(c,dx,xa,xb):
    inter=boxinterior(c,xa,xb)
    for y,x in zip(hy,hx):
        if 0<=x+dx<c.shape[1] and inter[y,x+dx]: c[y,x+dx]=c1[y,x]
# digit regions in crop coords
dig=(455,0,520,130)  # first digit area
three=(550,0,610,130)
def cleardigit(c):
    x0,y0,x1,y1=dig; c[y0:y1,x0:x1]=0
def paste3(c):
    lab,n=ndimage.label(c0[...,3]>40)
    best=None
    for k in range(1,n+1):
        ys,xs=np.where(lab==k)
        if xs.mean()>565 and (best is None or len(xs)>best[0]): best=(len(xs),k)
    m=lab==best[1]; ys,xs=np.where(m); dx=dig[0]+6-xs.min()
    c[ys,xs+dx]=c0[ys,xs]
c2=c1.copy(); addhatch(c2,145,150,300)
cleardigit(c2)
im=Image.fromarray(c2); d=ImageDraw.Draw(im)
pts=[(480,56),(486,45),(497,39),(508,42),(511,54),(505,70),(493,86),(479,104),(496,103),(514,102)]
import random; random.seed(3)
pts=[(x+random.uniform(-1,1),y+random.uniform(-1,1)) for x,y in pts]
d.line(pts,fill=(12,12,12,255),width=9,joint='curve')
for x,y in (pts[0],pts[-1]): d.ellipse((x-4,y-4,x+4,y+4),fill=(12,12,12,255))
c2=np.array(im)
c3=c2.copy(); addhatch(c3,288,295,445); cleardigit(c3); paste3(c3)
for a,n in [(c0,'prog0'),(c1,'prog1'),(c2,'prog2'),(c3,'prog3')]:
    Image.fromarray(a).save(OUT+n+'.png',optimize=True)
s=Image.new('RGBA',(X1-X0,4*(Y1-Y0)),(150,210,150,255))
for i,a in enumerate([c0,c1,c2,c3]): s.alpha_composite(Image.fromarray(a),(0,i*(Y1-Y0)))
s.convert('RGB').save('/tmp/claude-0/-home-user-caesar/7474d5dd-00d3-5131-b01a-5d29cff7faba/scratchpad/v/prog.jpg')
print(X0,Y0,X1-X0,Y1-Y0)
