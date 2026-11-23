import json
SEGS=[(0.00,10.25),(11.30,12.08),(12.80,16.00),(19.10,25.40)]
S=[(0.06,"良い男には／【理想】がある"),(1.09,"守るものと／立ち向かうものが"),(3.36,"そして／試された時"),
(4.52,"良い男は／《いい人》／じゃない"),(7.32,"良い男でいるのは／ずっと【難しい】"),
(11.42,"いちばんの／【人気者】には／なれない"),(13.60,"いつも／【愛想よく】は／いられない"),
(19.18,"時には／こう言うことだ"),(21.65,"「これを／【信じる】」"),(22.53,"「これは／自分のものだ」"),(24.05,"「あれは／《違う》」")]
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
