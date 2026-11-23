import onnxruntime as ort, numpy as np, cv2
s=ort.InferenceSession('/tmp/claude-0/-home-user-Box/040acad2-6470-5d27-96c4-1c28d2fc55c2/scratchpad/models/lama_fp32.onnx',providers=['CPUExecutionProvider'])
BAND=(500,590)
def text_mask(img):
    band=np.zeros(img.shape[:2],bool); band[BAND[0]:BAND[1]]=True
    m=((img.min(2)>195)&((img.max(2).astype(int)-img.min(2))<35)&band).astype(np.uint8)*255
    if m.sum()==0: return m
    m=cv2.dilate(m,np.ones((15,15),np.uint8))
    sh=np.zeros_like(m); sh[4:,4:]=m[:-4,:-4]   # 影（右下）も覆う
    return np.maximum(m,sh)
def clean(img,m=None):
    m=text_mask(img) if m is None else m
    if m.max()==0: return img
    out=img.copy(); xs=np.where(m.any(0))[0]
    y0=545-256
    xs0=sorted(set([max(0,min(1080-512,x)) for x in range(xs.min()-60, xs.max()+60, 380)]))
    for x0 in xs0:
        mw=(m[y0:y0+512,x0:x0+512]>0).astype(np.float32)
        if mw.sum()==0: continue
        win=out[y0:y0+512,x0:x0+512].astype(np.float32)/255
        r=s.run(None,{'image':win.transpose(2,0,1)[None],'mask':mw[None,None]})[0][0].transpose(1,2,0)
        sel=mw>0; o=out[y0:y0+512,x0:x0+512]; o[sel]=np.clip(r[sel],0,255).astype(np.uint8)
        m[y0:y0+512,x0:x0+512][sel]=0
    return out
