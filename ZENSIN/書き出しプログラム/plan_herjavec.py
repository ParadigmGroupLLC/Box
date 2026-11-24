import json
SEGS=[(0.00,5.35),(6.45,10.30)]
S=[(0.05,"良い営業は"),(1.22,"【機能】を売る"),(3.12,"すごい営業は"),(3.90,"【結果】を売る"),
(6.60,"そして／本当に／すごい営業は"),(9.30,"《感情》を売る")]
def s2r(x):
    acc=0
    for a,b in SEGS:
        if x<a: return acc
        if x<b: return acc+(x-a)
        acc+=b-a
    return acc
tot=sum(b-a for a,b in SEGS)
st=[round(s2r(a),2) for a,_ in S]
subs=[[st[i],round(st[i+1]-0.03 if i+1<len(st) else tot-0.05,2),t] for i,(_,t) in enumerate(S)]
json.dump({'segs':SEGS,'subs':subs,'total':tot},open('plan.json','w'),ensure_ascii=False)
print(round(tot,2)); [print(s) for s in subs]
