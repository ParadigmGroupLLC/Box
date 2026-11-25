import numpy as np, json
db=np.load('db.npy'); OFF=2060
PARTS=[(2092.0,2096.52),(2097.6,2101.5),(2067.8,2074.7),(2078.1,2091.9),(2112.3,2132.5),(2172.9,2185.15),(2193.15,2211.68)]
PRE,POST,CAP,K=0.07,0.09,0.20,0.30
s=db; fl=np.percentile(s,10); pk=np.percentile(s,90); thr=fl+K*(pk-fl)
idx=lambda t:int(round((t-OFF)*100))
# 区間の頭と尻の無音を落とす（声の始まりの PRE 前から、終わりの POST 後まで）
P2=[]
for A,B in PARTS:
    v=s[idx(A):idx(B)]>=thr
    on=np.nonzero(v)[0]
    a=max(A,A+on[0]/100-PRE); b=min(B,A+on[-1]/100+0.01+POST)
    P2.append((round(a,2),round(b,2)))
segs=[]
for A,B in P2:
    v=s[idx(A):idx(B)]<thr; cur=A; i=0
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
tot=sum(b-a for a,b in segs)
json.dump({'segs':segs,'subs':[],'total':tot},open('plan.json','w'))
print(P2); print(len(segs),round(tot,2))
