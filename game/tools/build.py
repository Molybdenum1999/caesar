import numpy as np, json, os
from PIL import Image, ImageDraw, ImageEnhance
from scipy import ndimage
SRC='/home/user/caesar/'
OUT='/home/user/caesar/game/assets/'
os.makedirs(OUT,exist_ok=True)
META={}
def load(n): return np.array(Image.open(SRC+n).convert('RGBA'))
def despeck(a,minpx=400):
    m=a[...,3]>20
    lab,n=ndimage.label(m)
    if n==0: return a
    sizes=ndimage.sum(m,lab,range(1,n+1))
    keep=np.isin(lab,1+np.where(sizes>=minpx)[0])
    a=a.copy(); a[~keep]=0; return a
def fillholes(a):
    # any transparent pixel not connected to the image border becomes white
    m=a[...,3]>60
    filled=ndimage.binary_fill_holes(m)
    holes=filled&~m
    a=a.copy()
    # composite white under semi-transparent pixels inside
    inside=filled
    al=a[...,3:4]/255.0
    rgb=a[...,:3]*al+255*(1-al)
    a[inside,:3]=rgb[inside]; a[inside,3]=255
    return a
def bbox(a,th=20):
    m=a[...,3]>th; ys,xs=np.where(m); return [int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1]
def save(a,name,box=None,scale=1.0,fmt='png',pad=2):
    if box is None: box=bbox(a)
    x0,y0,x1,y1=box; x0=max(0,x0-pad);y0=max(0,y0-pad);x1=min(a.shape[1],x1+pad);y1=min(a.shape[0],y1+pad)
    im=Image.fromarray(a[y0:y1,x0:x1].astype('uint8'))
    if scale!=1.0: im=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.LANCZOS)
    fn=name+'.'+fmt
    if fmt=='jpg': im.convert('RGB').save(OUT+fn,quality=82)
    else: im.save(OUT+fn,optimize=True)
    META[name]={'f':fn,'x':x0,'y':y0,'w':x1-x0,'h':y1-y0}
    return META[name]
def dark(a): return (a[...,3]>100)&(a[...,:3].sum(-1)<330)

# ---------- character parts ----------
def head_parts(src,name,pupils,mouthbox,extra=None):
    a=fillholes(despeck(load(src)))
    lab,n=ndimage.label(dark(a))
    for i,(kind,box) in enumerate(pupils):
        x0,y0,x1,y1=box
        m=np.zeros(a.shape[:2],bool)
        if kind=='comp':
            ids=set(np.unique(lab[y0:y1,x0:x1]))-{0}
            for k in ids:
                ys,xs=np.where(lab==k)
                if xs.min()>=x0-2 and xs.max()<=x1+2 and ys.min()>=y0-2 and ys.max()<=y1+2: m|=lab==k
        else:
            m[y0:y1,x0:x1]=dark(a)[y0:y1,x0:x1]
        m=ndimage.binary_dilation(m,iterations=1)
        sp=np.zeros_like(a); sp[m]=a[m]; sp[m,3]=255
        save(sp,f'{name}_pupil{i}')
        a[m,:3]=255; a[m,3]=255
    # mouth sprite (dark + interior white), head gets mouth whited
    x0,y0,x1,y1=mouthbox
    sub=a[y0:y1,x0:x1].copy()
    dm=dark(sub)
    sp=np.zeros_like(a); sp[y0:y1,x0:x1]=sub; 
    sp[y0:y1,x0:x1][~dm]=[255,255,255,255]
    # make outside-of-mouth white transparent-ish: keep only filled shape of dark strokes
    shape=ndimage.binary_fill_holes(ndimage.binary_closing(dm,iterations=3))|dm
    tmp=sp[y0:y1,x0:x1]; tmp[~shape]=0
    save(sp,f'{name}_mouth')
    a[y0:y1,x0:x1][shape]=[255,255,255,255]
    save(a,name)
    return a

head_parts('head.png','head1',[('comp',(536,468,568,540)),('box',(716,468,733,537))],(586,600,678,654))
head_parts('head2.png','head2',[('comp',(538,520,556,580)),('comp',(674,500,700,565))],(590,640,634,676))
hs=fillholes(despeck(load('h-smile.png'))); save(hs,'hsmile')
# blink overlay from h-smile eyes region
blk=hs.copy(); mm=np.zeros(blk.shape[:2],bool); mm[438:560,492:778]=True; blk[~mm]=0
save(blk,'blink1')
for n,o in [('body.png','body1'),('body2.png','body2'),('neck.png','neck1'),('neck2.png','neck2')]:
    save(fillholes(despeck(load(n))),o)
b=fillholes(despeck(load('bunches.png')))
L=b.copy();L[:,640:]=0; R=b.copy();R[:,:640]=0
save(L,'tailL');save(R,'tailR')

# ---------- UI ----------
bg=Image.open(SRC+'background.png').convert('RGB')
bg=ImageEnhance.Brightness(bg).enhance(0.62); bg=ImageEnhance.Contrast(bg).enhance(1.05)
bg.resize((1600,1000),Image.LANCZOS).save(OUT+'background.jpg',quality=80)
def despeck_top(a,minpx):
    m=a[...,3]>20; lab,n=ndimage.label(m); ys,xs=np.where(m); y0,y1=ys.min(),ys.max()
    a=a.copy()
    for k in range(1,n+1):
        yy,xx=np.where(lab==k)
        if len(yy)<minpx and (len(yy)<12 or yy.max()<y0+(y1-y0)*0.6): a[lab==k]=0
    return a
def ui(src,name,scale=0.5,fill=True,minpx=200,fmt='png'):
    a=despeck_top(load(src),minpx) if src.startswith(('file','img')) else despeck(load(src),minpx)
    if fill: a=fillholes(a)
    return save(a,name,scale=scale,fmt=fmt)
ui('login page.png','login',0.6)
ui('dkk.png','panel',0.5)
ui('chatbox-m.png','chatm',0.5)
ui('chatbox-s.png','chats',0.5)
ui('upload.png','upload',0.6)
ui('success.png','success',0.6)
ui('mouse.png','cursor',0.25)
for i in range(1,6): ui(f'file{i}.png',f'file{i}',0.5,fill=False,minpx=200)
ui('img.png','img',0.5,fill=False,minpx=200)
ui('file-open.png','fileopen',0.5)
ui('changeclothes.png','win4',0.5)
ui('7.png','win5',0.5)
ui('posterbox.png','win1',0.5)
ui('ida.png','winimg',0.5)
# page frames: drop faint ghost overlay
def frame(src,name):
    a=load(src); a[a[...,3]<120]=0; a=fillholes(despeck(a,200)); return a
p=frame('page.png','win2'); save(p,'win2',scale=0.5)
p=frame('pages.png','win3')
# split arrows & page number out of the diary frame
bb=bbox(p)
def cutout(a,box,name):
    x0,y0,x1,y1=box; sp=np.zeros_like(a); sp[y0:y1,x0:x1]=a[y0:y1,x0:x1]; save(sp,name,scale=0.5)
    a[y0:y1,x0:x1][a[y0:y1,x0:x1,3]>0]=[255,255,255,255]
META['_diarybox']=bb
json.dump(META,open(OUT+'meta.json','w'),indent=1)
np.save('/tmp/claude-0/-home-user-caesar/7474d5dd-00d3-5131-b01a-5d29cff7faba/scratchpad/pages.npy',p)
print(json.dumps(META))
cutout(p,(1228,1715,1412,1842),'arrowL')
cutout(p,(2608,1678,2818,1822),'arrowR')
x0,y0,x1,y1=(2380,1712,2565,1812); p[y0:y1,x0:x1][p[y0:y1,x0:x1,3]>0]=[255,255,255,255]
save(p,'win3',scale=0.5)
json.dump(META,open(OUT+'meta.json','w'),indent=1)
# ---- hover (open folder) variants, same box as closed icon ----
fo=Image.open(SRC+'file-open.png').convert('RGBA'); fo=fo.crop(fo.getchannel('A').point(lambda v:255 if v>20 else 0).getbbox())
for i in range(1,6):
    m=META[f'file{i}']; a=despeck_top(load(f'file{i}.png'),200)[m['y']:m['y']+m['h'],m['x']:m['x']+m['w']].copy()
    prof=(a[...,3]>40).sum(1)
    rows=np.where(prof>0)[0]
    # biggest empty gap -> split between folder and label
    gaps=[(rows[k+1]-rows[k],rows[k]) for k in range(len(rows)-1)]
    g,split=max(gaps); split=int(split)+1
    folder=a[:split]; ys,xs=np.where(folder[...,3]>40)
    fx0,fx1,fy1=xs.min(),xs.max(),ys.max()
    out=a.copy(); out[:split]=0
    out=np.pad(out,((0,0),(40,40),(0,0))); fx0+=40; fx1+=40
    im=Image.fromarray(out)
    tw=int((fx1-fx0)*1.08); th=int(fo.height*tw/fo.width)
    f2=fo.resize((tw,th),Image.LANCZOS)
    cx=(fx0+fx1)//2
    im.alpha_composite(f2,(max(0,cx-tw//2),max(0,fy1-th+6)))
    im=im.resize((round(im.width*0.5),round(im.height*0.5)),Image.LANCZOS); im.save(OUT+f'file{i}_open.png',optimize=True)
    print('file',i,'split',split,g)
# ---- clothes button cut out of the window ----
w4=fillholes(despeck(load('changeclothes.png'),200))
bx=(1390,630,1930,990)
x0,y0,x1,y1=bx; reg=w4[y0:y1,x0:x1]
dm=dark(reg); lab,n=ndimage.label(dm)
sizes=ndimage.sum(dm,lab,range(1,n+1)); k=1+int(np.argmax(sizes))
oval=ndimage.binary_fill_holes(lab==k)
btn=np.zeros_like(w4); btn[y0:y1,x0:x1][oval]=reg[oval]
save(btn,'btn4',scale=0.5)
w4[y0:y1,x0:x1][ndimage.binary_dilation(oval,iterations=4)]=[255,255,255,255]
save(w4,'win4',scale=0.5)
json.dump(META,open(OUT+'meta.json','w'),indent=1)
# ---- login: lift the hand-drawn name box out of the frame so it can be re-centred under Caesar ----
lg=fillholes(despeck(load('login page.png'),200))
bx=(966,1230,2118,1458); x0,y0,x1,y1=bx
sp=np.zeros_like(lg); sp[y0:y1,x0:x1]=lg[y0:y1,x0:x1]
d=dark(sp); sp[~d]=0; save(sp,'loginbox',scale=0.6)
lg[y0:y1,x0:x1]=[255,255,255,255]
save(lg,'login',scale=0.6)
json.dump(META,open(OUT+'meta.json','w'),indent=1)
