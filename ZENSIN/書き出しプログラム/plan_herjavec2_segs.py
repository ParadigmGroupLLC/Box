import numpy as np, json
db=np.load('db.npy'); OFF=2428  # db.npy は 2428 秒から
PARTS=[(2432.42,2437.45),(2439.10,2466.65),(2471.50,2476.12)]
PRE,POST,CAP,K=0.07,0.09,0.20,0.30
s=db; fl=np.percentile(s,10); pk=np.percentile(s,90); thr=fl+K*(pk-fl)
segs=[]
for A,B in PARTS:
    v=s[int((A-OFF)*100):int((B-OFF)*100)]<thr; cur=A; i=0
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
print(len(segs),round(tot,2))
# 「feelings」の s（高い音で、帯域の音量に出ない）を切らないよう、2449.2 のつなぎ目はつなげる
m=[]
for a,b in segs:
    if m and abs(m[-1][1]-2449.21)<0.05: m[-1]=(m[-1][0],b)
    else: m.append((a,b))
segs=m; tot=sum(b-a for a,b in segs)
json.dump({'segs':segs,'subs':[],'total':tot},open('plan.json','w'))
print(len(segs),round(tot,2))
