import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D=int(sys.argv[1]) if len(sys.argv)>1 else 160
W,H=1080,1920
base=np.asarray(Image.open('base.png').convert('RGB')).astype(np.float32)
mask=np.asarray(Image.open('mask_u2net_human_seg.png').convert('L').filter(ImageFilter.GaussianBlur(2))).astype(np.float32)/255
# row mapping: final y -> source y
YB=1480
ys=np.arange(H,dtype=np.float32)
src=np.where(ys<YB, ys+D, (YB+D)+(ys-YB)*(H-1-(YB+D))/(H-1-YB))
def remap(a):
    y0=np.floor(src).astype(int); y1=np.minimum(y0+1,H-1); t=(src-y0)[:,None]
    if a.ndim==3: t=t[:,:,None]
    return a[y0]*(1-t)+a[y1]*t
sh=remap(base); shm=remap(mask)
# background: original at top band, shifted below, blended
w=np.clip((ys-300)/180,0,1)[:,None,None]
bg=base*(1-w)+sh*w
m=shm[:,:,None]
out=sh*m+bg*(1-m)
img=Image.fromarray(np.clip(out,0,255).astype(np.uint8))
img.save('person_moved.png')
# --- text ---
F='fonts/'
TITLE=F+'VdGBAYIAV6gnpUpoWwNkYvrugw9RuM1y55sK.ttf'   # Rounded Mplus 1c Medium
SUB=F+'VdGBAYIAV6gnpUpoWwNkYvrugw9RuM064ZsK.ttf'     # Rounded Mplus 1c Bold
def text_layer(txt, font, size, track, sx, stroke):
    ft=ImageFont.truetype(font,size)
    ws=[ft.getlength(c) for c in txt]
    tw=int(sum(ws)+track*(len(txt)-1))+stroke*4+20
    asc,desc=ft.getmetrics(); th=asc+desc+stroke*4+20
    L=Image.new('RGBA',(tw,th),(0,0,0,0)); d=ImageDraw.Draw(L)
    x=10+stroke*2
    for c,wc in zip(txt,ws):
        d.text((x,10+stroke*2),c,font=ft,fill='white',stroke_width=stroke,stroke_fill=(17,17,17))
        x+=wc+track
    L=L.crop(L.getbbox())
    if sx!=1: L=L.resize((int(L.width*sx),L.height),Image.LANCZOS)
    return L
def place(img,L,cx,top,shadow=6):
    sh=Image.new('RGBA',L.size,(0,0,0,0)); a=L.split()[3]
    sh.putalpha(a.point(lambda v:int(v*0.45)))
    sh=sh.filter(ImageFilter.GaussianBlur(shadow))
    x=int(cx-L.width/2)
    img.alpha_composite(sh,(x+3,top+4)); img.alpha_composite(L,(x,top))
    return (x,top,x+L.width,top+L.height)
img=img.convert('RGBA')
T=text_layer('JUST DO IT',TITLE,112,-6,1.0,4)
# fit width/height to reference box 652x97
T=T.resize((664,97),Image.LANCZOS)
b1=place(img,T,540,872)
S=text_layer('~とにかくやってみよう~',SUB,44,9,1.0,4)
S=S.resize((610,int(S.height*610/S.width)),Image.LANCZOS)
b2=place(img,S,536,1012,4)
print(b1,b2,S.size)
img.convert('RGB').save('ichiro_cover_v2.png')
