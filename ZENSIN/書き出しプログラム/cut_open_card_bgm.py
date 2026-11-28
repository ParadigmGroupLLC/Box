import subprocess,numpy as np,re,sys
W,H=1080,1920
FPS=24000/1001
START_F=106; T0=START_F*1001/24000          # 「良い営業は」の場面の最初のコマ
OPEN=0.6                                    # カードが開く長さ
CX0,CX1,CY0,CY1=30,1050,673,1247            # カードの位置
SUB_BOTTOM=718                               # 字幕のいちばん下
def run(a): subprocess.run(a,check=True)
def lufs(f):
    e=subprocess.run(['ffmpeg','-hide_banner','-i',f,'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS',e)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS',e)[-1])
X,S,K=float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3])
# ---- 音 ----
run(['ffmpeg','-loglevel','error','-y','-ss',f'{T0:.6f}','-i','src.mp4','-vn','-ac','2','-ar','48000','-c:a','pcm_s16le','v0.wav'])
li,_=lufs('v0.wav')
run(['ffmpeg','-loglevel','error','-y','-i','v0.wav','-af',f'volume={-14.5-li}dB,alimiter=limit=0.84:attack=5:release=50:level=disabled','-c:a','pcm_s16le','vA.wav'])
D=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','vA.wav'],capture_output=True,text=True).stdout)
env=f"volume='if(lt(t,{K-3:.2f}),1,if(lt(t,{K:.2f}),1-0.3*(t-{K-3:.2f})/3,0.7))':eval=frame"
run(['ffmpeg','-loglevel','error','-y','-i','vA.wav','-ss',str(S),'-t',str(D),'-i','exp.wav','-filter_complex',
 f"[1:a]aformat=channel_layouts=stereo,volume={X}dB,{env},afade=t=in:d=1.5,afade=t=out:st={D-2.0}:d=2.0[b];[b][0:a]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=300[bd]",
 '-map','[bd]','-c:a','pcm_s16le','bdA.wav'])
def load(f): return np.frombuffer(subprocess.run(['ffmpeg','-loglevel','error','-i',f,'-ac','1','-ar','8000','-f','f32le','-'],capture_output=True).stdout,np.float32)
v=load('vA.wav'); b=load('bdA.wav'); sr=8000
db=lambda x,s:20*np.log10(np.sqrt(np.mean(x[s]**2))+1e-9)
print('LUFS diff',round(lufs('vA.wav')[0]-lufs('bdA.wav')[0],1))
print('voice-bgm per 4s:',' '.join(f'{t}:{db(v,slice(t*sr,(t+4)*sr))-db(b,slice(t*sr,(t+4)*sr)):.1f}' for t in range(0,int(D)-1,4)))
TGT={'mix_bgm.wav':-13.4,'mix_nobgm.wav':-13.8}
for name,inputs,fc in [('mix_bgm.wav',['vA.wav','bdA.wav','intro.wav'],'[0:a][1:a][2:a]amix=inputs=3:duration=first:normalize=0[m]'),
                       ('mix_nobgm.wav',['vA.wav','intro.wav'],'[0:a][1:a]amix=inputs=2:duration=first:normalize=0[m]')]:
    a=[]; [a.extend(['-i',i]) for i in inputs]
    run(['ffmpeg','-loglevel','error','-y',*a,'-filter_complex',fc,'-map','[m]','-c:a','pcm_s16le','pre.wav'])
    pi,_=lufs('pre.wav')
    run(['ffmpeg','-loglevel','error','-y','-i','pre.wav','-af',f'volume={TGT[name]-pi}dB,alimiter=limit=0.80:attack=5:release=50:level=disabled,afade=t=in:d=0.02,afade=t=out:st={D-0.6}:d=0.6','-c:a','pcm_s16le',name])
# ---- 映像：最初の0.6秒でカードを中央から上下に開く ----
C=np.frombuffer(subprocess.run(['ffmpeg','-loglevel','error','-i','src.mp4','-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout,np.uint8).reshape(H,W,3).copy()
dec=subprocess.Popen(['ffmpeg','-loglevel','error','-ss',f'{T0:.6f}','-i','src.mp4','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','24000/1001','-i','-',
    '-c:v','libx264','-crf','14','-preset','medium','-pix_fmt','yuv420p','video_only.mp4'],stdin=subprocess.PIPE)
BG=None
n=0; cy=(CY0+CY1)/2; ch=CY1-CY0
while True:
    buf=dec.stdout.read(W*H*3)
    if len(buf)<W*H*3: break
    F=np.frombuffer(buf,np.uint8).reshape(H,W,3).copy()
    if BG is None: BG=F[CY0:SUB_BOTTOM+1,CX0:CX1].copy()   # 字幕が出る前の写真（最初のコマ）
    t=n/FPS
    if t<OPEN:
        p=t/OPEN; p=p*p*(3-2*p)                     # なめらかに開く
        half=ch*p/2; b0=int(round(cy-half)); b1=int(round(cy+half))
        out=F.copy()
        for (y0,y1) in [(CY0,b0),(b1,CY1)]:
            if y1<=y0: continue
            reg=C[y0:y1,CX0:CX1].copy()             # 閉じた状態（背景・ロゴ）
            # 字幕がカードに少しかかる所は、新しい字幕を残す
            ys=slice(y0,min(y1,SUB_BOTTOM+1))
            if ys.stop>ys.start:
                f=F[ys,CX0:CX1].astype(float); Bk=BG[ys.start-CY0:ys.stop-CY0].astype(float)
                lf=f.mean(2); lb=Bk.mean(2)
                a=np.clip((lf-lb)/np.maximum(238-lb,1),0,1); a=np.where(a<0.25,0,a)[...,None]   # 字幕の濃さ
                txt=np.clip((f-(1-a)*Bk),0,255)                          # 写真を引いて黒の上に置く
                reg[:ys.stop-y0]=txt.astype(np.uint8)
            out[y0:y1,CX0:CX1]=reg
        F=out
    enc.stdin.write(F.tobytes()); n+=1
enc.stdin.close(); enc.wait(); dec.wait()
print('frames',n,'dur',n/FPS,'audio',D)
for name,suf in [('mix_bgm.wav',''),('mix_nobgm.wav','_BGMなし')]:
    out=f'ZENSIN_ロバート・ハージャベック_本当にすごい営業は感情を売る_良い営業はから{suf}.mp4'
    run(['ffmpeg','-loglevel','error','-y','-i','video_only.mp4','-i',name,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-shortest','-movflags','+faststart',out])
    print(out, lufs(out))
