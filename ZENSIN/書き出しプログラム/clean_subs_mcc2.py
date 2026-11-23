import subprocess, numpy as np, cv2, sys
from inpaint_lib import clean, text_mask
W=H=1080
def frames():
    p=subprocess.Popen(['ffmpeg','-v','error','-i','src/v.mp4','-vf','crop=1080:1080:0:420','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    while True:
        b=p.stdout.read(W*H*3)
        if len(b)<W*H*3: break
        yield np.frombuffer(b,np.uint8).reshape(H,W,3).copy()
F=list(frames()); n=len(F); print('frames',n,flush=True)
M=[text_mask(f) for f in F]
MM=[np.maximum.reduce(M[max(0,i-3):i+4]) for i in range(n)]
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1080','-r','30','-i','-','-i','src/v.mp4','-map','0:v','-map','1:a','-c:v','libx264','-crf','12','-preset','medium','-pix_fmt','yuv420p','-c:a','copy','clean.mp4'],stdin=subprocess.PIPE)
for i,(f,m) in enumerate(zip(F,MM)):
    enc.stdin.write(clean(f,m.copy()).tobytes())
    if i%30==0: print(i,'/',n,flush=True)
enc.stdin.close(); enc.wait(); print('done')
