import numpy as np, json, sys
d=sys.argv[1]
sm=np.load(f'{d}/env.npy')
P=json.load(open(f'{d}/plan.json'))
starts=[s[0] for s in P['subs']]
new=[]
for idx,a in enumerate(starts):
    i=int(a*100)
    fl=np.percentile(sm[max(0,i-300):i+300],15); pk=np.percentile(sm[max(0,i-300):i+300],85)
    thr=fl+0.35*(pk-fl)
    lo=max(0,i-30); hi=min(len(sm),i+80)
    low=sm[lo:hi]<thr
    runs=[];j=0
    while j<len(low):
        if low[j]:
            k=j
            while k<len(low) and low[k]: k+=1
            runs.append(((lo+j)/100,(lo+k)/100)); j=k
        else: j+=1
    b=a
    cand=[(s,e) for s,e in runs if e-s>=0.15 and s<=a+0.15 and e>a+0.05 and e<=a+0.8]
    if cand:
        s,e=cand[0]; b=round(e-0.05,2)
    if idx>0 and b<=new[-1]+0.4: b=a
    new.append(b)
subs=[]
for i,(a,b,t) in enumerate(P['subs']):
    st=new[i]; en=new[i+1]-0.03 if i+1<len(new) else P['total']-0.05
    subs.append([round(st,2),round(en,2),t])
    if abs(st-a)>0.01: print(f'{a:6.2f} -> {st:6.2f}  {t}')
P['subs']=subs
json.dump(P,open(f'{d}/plan_refined.json','w'),ensure_ascii=False)
