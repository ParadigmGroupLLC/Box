import numpy as np, json
db=np.load('db.npy'); sm=np.convolve(db,np.ones(3)/3,mode='same')
PARTS=[(126.30,158.40),(175.05,191.60),(227.95,247.25)]
PRE,POST,CAP=0.07,0.09,0.20  # 2回目（「間をもっと短くして」）。1回目は 0.10,0.14,0.36
def floor_thr(a,b):
    s=sm[int(a*100):int(b*100)]; fl=np.percentile(s,10); pk=np.percentile(s,90); return fl+0.30*(pk-fl)
segs=[]
for A,B in PARTS:
    thr=floor_thr(A,B)
    v=sm[int(A*100):int(B*100)]<thr
    cur=A; i=0
    while i<len(v):
        if v[i]:
            j=i
            while j<len(v) and v[j]: j+=1
            p0,p1=A+i/100,A+j/100
            if p1-p0>CAP and p0>A+0.05 and p1<B-0.05:
                segs.append((round(cur,2),round(p0+POST,2))); cur=p1-PRE
            i=j
        else: i+=1
    segs.append((round(cur,2),B))
# 小さい声の語が削れた所は、つなぎを戻す（risks・fail・Graduates）、large の頭を少し前から
S=[list(x) for x in segs]
for a_end,b_start in [(156.65,157.17),(185.42,186.44),(228.41,229.02)]:
    for i in range(len(S)-1):
        if abs(S[i][1]-a_end)<0.01 and abs(S[i+1][0]-b_start)<0.01:
            S[i][1]=S[i+1][1]; del S[i+1]; break
for x in S:
    if abs(x[0]-180.28)<0.01: x[0]=180.12
segs=[tuple(x) for x in S]
tot=sum(b-a for a,b in segs)
json.dump({'segs':segs,'subs':[],'total':tot},open('plan.json','w'))
print(len(segs),round(tot,2)); print(segs)
