"""Pre-render 'boiling line' frames of crashing.jpg (the same look as an SVG
feTurbulence + feDisplacementMap filter, but baked so the browser only swaps images)."""
import numpy as np
from PIL import Image
from scipy import ndimage
SRC='/home/user/caesar/crashing.jpg'; OUT='/home/user/caesar/game/assets/'
W,H=1600,900; SCALE=10.0      # displacement in px, matching scale="10" on a 1600x900 viewBox
base=np.array(Image.open(SRC).convert('L').resize((W,H),Image.LANCZOS)).astype(np.float32)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
def field(rng):
    # two octaves of smooth noise, roughly baseFrequency 0.014 (features ~70px)
    f=np.zeros((H,W),np.float32)
    for sigma,amp in ((22,1.0),(11,.5)):
        n=ndimage.gaussian_filter(rng.standard_normal((H,W)).astype(np.float32),sigma)
        f+=amp*n/(np.abs(n).max()+1e-6)
    return f/1.5
for k in range(6):
    rng=np.random.default_rng(k+2)
    dx,dy=field(rng)*SCALE,field(rng)*SCALE
    out=ndimage.map_coordinates(base,[yy+dy,xx+dx],order=1,mode='nearest')
    Image.fromarray(out.clip(0,255).astype(np.uint8)).save(OUT+f'crash{k}.jpg',quality=80)
print('ok')
