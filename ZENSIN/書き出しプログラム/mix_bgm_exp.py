import subprocess,re,numpy as np,sys
def run(a): subprocess.run(a,check=True)
def lufs(f):
    e=subprocess.run(['ffmpeg','-hide_banner','-i',f,'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS',e)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS',e)[-1])
# 声：-14.5 LUFS ＋リミッター
run(['ffmpeg','-loglevel','error','-y','-i','cutA.wav','-ac','2','-ar','48000','-c:a','pcm_s16le','v0.wav'])
li,_=lufs('v0.wav')
run(['ffmpeg','-loglevel','error','-y','-i','v0.wav','-af',f'volume={-14.5-li}dB,alimiter=limit=0.84:attack=5:release=50:level=disabled','-c:a','pcm_s16le','vA.wav'])
D=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','vA.wav'],capture_output=True,text=True).stdout)
X=float(sys.argv[1]); S=float(sys.argv[2])
K=float(sys.argv[3]); env=f"volume='if(lt(t,{K-3:.2f}),1,if(lt(t,{K:.2f}),1-0.3*(t-{K-3:.2f})/3,0.7))':eval=frame"
run(['ffmpeg','-loglevel','error','-y','-i','vA.wav','-ss',str(S),'-t',str(D),'-i','bgm/exp.wav','-filter_complex',
 f"[1:a]aformat=channel_layouts=stereo,volume={X}dB,{env},afade=t=in:d=1.5,afade=t=out:st={D-2.0}:d=2.0[b];[b][0:a]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=300[bd]",
 '-map','[bd]','-c:a','pcm_s16le','bdA.wav'])
def load(f): return np.frombuffer(subprocess.run(['ffmpeg','-loglevel','error','-i',f,'-ac','1','-ar','8000','-f','f32le','-'],capture_output=True).stdout,np.float32)
v=load('vA.wav'); b=load('bdA.wav'); sr=8000
print('voice-bgm dB per 4s:',end=' ')
for t0 in range(0,52,4):
    s=slice(t0*sr,(t0+4)*sr); db=lambda x:20*np.log10(np.sqrt(np.mean(x[s]**2))+1e-9)
    print(f'{t0}:{db(v)-db(b):.1f}', end='  ')
print('\nLUFS diff', round(lufs('vA.wav')[0]-lufs('bdA.wav')[0],1))
run(['ffmpeg','-loglevel','error','-y','-i','vA.wav','-i','bdA.wav','-i','intro.wav','-filter_complex','[0:a][1:a][2:a]amix=inputs=3:duration=first:normalize=0[m]','-map','[m]','-c:a','pcm_s16le','premix.wav'])
pi,_=lufs('premix.wav'); g=-13.4-pi
run(['ffmpeg','-loglevel','error','-y','-i','premix.wav','-af',f'volume={g}dB,alimiter=limit=0.84:attack=5:release=50:level=disabled,afade=t=in:d=0.08,afade=t=out:st={D-0.6}:d=0.6','-c:a','pcm_s16le','mix_bgm.wav'])
# BGMなし版
run(['ffmpeg','-loglevel','error','-y','-i','vA.wav','-i','intro.wav','-filter_complex','[0:a][1:a]amix=inputs=2:duration=first:normalize=0[m]','-map','[m]','-c:a','pcm_s16le','premix0.wav'])
pi,_=lufs('premix0.wav')
run(['ffmpeg','-loglevel','error','-y','-i','premix0.wav','-af',f'volume={-14.0-pi}dB,alimiter=limit=0.84:attack=5:release=50:level=disabled,afade=t=in:d=0.08,afade=t=out:st={D-0.6}:d=0.6','-c:a','pcm_s16le','mix_nobgm.wav'])
print('final bgm',lufs('mix_bgm.wav'),'nobgm',lufs('mix_nobgm.wav'),'dur',D)
