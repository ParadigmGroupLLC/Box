# 元の音（会場の音楽入り）をそのまま使う。こちらでBGMは足さない。導入音と合わせて -14 LUFS、ピーク -1 dBTP 以内
import subprocess,re
def run(a): subprocess.run(a,check=True)
def lufs(f):
    e=subprocess.run(['ffmpeg','-hide_banner','-i',f,'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS',e)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS',e)[-1])
run(['ffmpeg','-loglevel','error','-y','-i','cutA.wav','-ac','2','-ar','48000','-c:a','pcm_s16le','v0.wav'])
li,_=lufs('v0.wav')
run(['ffmpeg','-loglevel','error','-y','-i','v0.wav','-af',f'volume={-14.5-li}dB,alimiter=limit=0.84:attack=5:release=50:level=disabled','-c:a','pcm_s16le','vA.wav'])
D=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','vA.wav'],capture_output=True,text=True).stdout)
run(['ffmpeg','-loglevel','error','-y','-i','vA.wav','-i','intro.wav','-filter_complex','[0:a][1:a]amix=inputs=2:duration=first:normalize=0[m]','-map','[m]','-c:a','pcm_s16le','premix0.wav'])
pi,_=lufs('premix0.wav')
run(['ffmpeg','-loglevel','error','-y','-i','premix0.wav','-af',f'volume={-14.0-pi}dB,alimiter=limit=0.84:attack=5:release=50:level=disabled,afade=t=in:d=0.08,afade=t=out:st={D-0.6}:d=0.6','-c:a','pcm_s16le','mix.wav'])
print('final',lufs('mix.wav'),'dur',D)
