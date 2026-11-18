import subprocess, numpy as np, json, sys
d=sys.argv[1]
sr=16000
x=np.frombuffer(subprocess.run(['ffmpeg','-loglevel','error','-i',f'{d}/cutA.wav','-af','highpass=f=250,lowpass=f=3500','-f','f32le','-ac','1','-ar',str(sr),'-'],capture_output=True).stdout,np.float32)
hop=160;win=400
n=(len(x)-win)//hop
db=np.array([20*np.log10(np.sqrt(np.mean(x[i*hop:i*hop+win]**2))+1e-9) for i in range(n)])
sm=np.convolve(db,np.ones(3)/3,mode='same')
np.save(f'{d}/env.npy',sm)
P=json.load(open(f'{d}/plan.json'))
for a,b,t in P['subs']:
    i=int(a*100)
    lo=max(0,i-60); hi=min(len(sm),i+60)
    seg=sm[lo:hi]
    # local floor and peaks
    fl=np.percentile(sm[max(0,i-300):i+300],15); pk=np.percentile(sm[max(0,i-300):i+300],85)
    thr=fl+0.35*(pk-fl)
    # find low runs (pauses) in window
    low=seg<thr
    runs=[];j=0
    while j<len(seg):
        if low[j]:
            k=j
            while k<len(seg) and low[k]: k+=1
            if k-j>=4: runs.append(((lo+j)/100,(lo+k)/100))
            j=k
        else: j+=1
    print(f'{a:6.2f} {t[:14]:16s} thr={thr:5.1f} pauses={runs}')
