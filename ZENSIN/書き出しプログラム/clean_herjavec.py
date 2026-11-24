import numpy as np, cv2, subprocess, onnxruntime as ort
s=ort.InferenceSession('/tmp/claude-0/-home-user-Box/040acad2-6470-5d27-96c4-1c28d2fc55c2/scratchpad/models/lama_fp32.onnx',providers=['CPUExecutionProvider'])
F=np.load('frames.npy'); M=np.load('masks.npy'); n=len(F); H,W=F.shape[1:3]
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-i','src/v.mp4','-map','0:v','-map','1:a','-c:v','libx264','-crf','12','-pix_fmt','yuv420p','-c:a','copy','clean.mp4'],stdin=subprocess.PIPE)
for i in range(n):
    src=F[max(i,18)] if i<18 else F[i]
    m=M[max(i,18)].copy() if i<18 else M[i].copy()
    out=src.copy()
    if i<=334 and m.max()>0:
        for y0 in (0,H-512):
            for x0 in (0,(W-512)//2,W-512):
                mw=(m[y0:y0+512,x0:x0+512]>0).astype(np.float32)
                if mw.sum()==0: continue
                win=out[y0:y0+512,x0:x0+512].astype(np.float32)/255
                r=s.run(None,{'image':win.transpose(2,0,1)[None],'mask':mw[None,None]})[0][0].transpose(1,2,0)
                sel=mw>0; o=out[y0:y0+512,x0:x0+512]; o[sel]=np.clip(r[sel],0,255).astype(np.uint8)
                m[y0:y0+512,x0:x0+512][sel]=0
    enc.stdin.write(out.tobytes())
    if i%20==0: print(i,'/',n,flush=True)
enc.stdin.close(); enc.wait(); print('done')
