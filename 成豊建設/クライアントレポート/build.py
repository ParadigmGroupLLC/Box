import datetime as dt, statistics as st, html
from data import *
def jst(s): return dt.datetime.fromisoformat(s)+dt.timedelta(hours=9)
F=lambda v:f"{v:,}"
reels=[r for r in IG if r[1]=='REELS']
ig_total=sum(r[3] for r in IG); ig_reach=sum(r[4] for r in IG)
ig_med=st.median([r[3] for r in reels])
tt_total=sum(r[2] for r in TT); tt_med=st.median([r[2] for r in TT])
ig90=sum(IG_DAILY); tt90=sum(TT_DAILY)
def bars(vals,start,w=700,h=170,color='#1D5D89',cap=None):
    n=len(vals); mx=cap or max(vals); bw=w/n
    out=[f'<svg viewBox="0 0 {w} {h+24}" width="100%" role="img">']
    for i,v in enumerate(vals):
        vh=min(v,mx)/mx*h
        out.append(f'<rect x="{i*bw+0.5:.1f}" y="{h-vh:.1f}" width="{max(bw-1,1):.1f}" height="{vh:.1f}" fill="{color}"/>')
        if v>mx: out.append(f'<text x="{i*bw+bw/2:.1f}" y="10" font-size="10" text-anchor="middle" fill="#333">{F(v)}↑</text>')
    d0=dt.date.fromisoformat(start)
    for i in range(0,n,15):
        d=d0+dt.timedelta(days=i)
        out.append(f'<text x="{i*bw:.1f}" y="{h+16}" font-size="10" fill="#555">{d.month}/{d.day}</text>')
    out.append('</svg>'); return ''.join(out)
def kind(t):
    A=['言わないこと','共感','風習','1日','ズレてる','究極','スケジュール','重機','綺麗に繋がる','辞める理由','昭和すぎ','令和']
    I=['聞いてみた','インタビュー','レジェンド','リアル','本音を']
    return 'あるある・業界の中の話' if any(k in t for k in A) else 'インタビュー' if any(k in t for k in I) else '会社・採用の紹介'
rows_ig=''.join(f"<tr><td>{jst(r[0]):%m/%d}</td><td>{jst(r[0]):%H:%M}</td><td class=l>{html.escape(r[2])}</td><td>{F(r[3])}</td><td>{F(r[4])}</td><td>{r[5]}</td><td>{r[6]}</td><td>{'' if r[7] is None else f'{r[7]*100:.0f}%'}</td></tr>" for r in sorted(IG,key=lambda r:r[0],reverse=True))
rows_tt=''.join(f"<tr><td>{jst(r[0]):%m/%d}</td><td>{jst(r[0]):%H:%M}</td><td class=l>{html.escape(r[1])}</td><td>{F(r[2])}</td><td>{F(r[3])}</td><td>{r[4]}</td><td>{r[5]}</td><td>{r[6]*100:.1f}%</td></tr>" for r in sorted(TT,key=lambda r:r[0],reverse=True))
# 種類
from collections import defaultdict
g=defaultdict(list)
for r in reels: g[kind(r[2])].append(r)
rows_kind=''.join(f"<tr><td class=l>{k}</td><td>{len(v)}</td><td>{F(int(st.median([x[3] for x in v])))}</td><td>{st.mean([x[7] for x in v])*100:.0f}%</td></tr>" for k,v in sorted(g.items(),key=lambda kv:-st.median([x[3] for x in kv[1]])))
# 時間
h=defaultdict(list)
for r in reels: h[jst(r[0]).hour].append(r[3])
ht=defaultdict(list)
for r in TT: ht[jst(r[0]).hour].append((r[2],r[4]))
rows_hour=''.join(f"<tr><td>{k}時台</td><td>{len(h.get(k,[]))}</td><td>{F(int(st.median(h[k]))) if k in h else '—'}</td><td>{len(ht.get(k,[]))}</td><td>{F(int(st.median([a for a,b in ht[k]]))) if k in ht else '—'}</td><td>{int(st.median([b for a,b in ht[k]])) if k in ht else '—'}</td></tr>" for k in sorted(set(h)|set(ht)))
# 年代
tot=sum(sum(v) for v in IG_AGE.values())
rows_age=''.join(f"<tr><td>{a}</td><td>{m}</td><td>{f}</td><td>{u}</td><td>{m+f+u}（{(m+f+u)/tot*100:.0f}%）</td></tr>" for a,(m,f,u) in IG_AGE.items())
rows_ttage=''.join(f"<tr><td>{a}</td><td>{p}%</td></tr>" for a,p in TT_AGE.items())
top_ig=max(IG,key=lambda r:r[3]); top_tt=max(TT,key=lambda r:r[2])
css="""
@page{size:A4;margin:14mm 12mm}
body{font-family:'Noto Sans CJK JP','Noto Sans JP',sans-serif;color:#333;background:#fff;font-size:10.5pt;line-height:1.55}
h1{font-size:19pt;color:#1D5D89;margin:0 0 2mm}
h2{font-size:13pt;color:#1D5D89;border-bottom:2px solid #1D5D89;padding-bottom:1mm;margin:7mm 0 3mm}
.sub{color:#555;font-size:9.5pt}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm;margin:3mm 0}
.tile{border:1px solid #d5e1ea;border-radius:3mm;padding:2.5mm 3mm;background:#f6f9fb}
.tile .k{font-size:8.5pt;color:#555}.tile .v{font-size:16pt;font-weight:700;color:#1D5D89}.tile .n{font-size:8pt;color:#555}
table{border-collapse:collapse;width:100%;font-size:8.2pt;margin:2mm 0}
.blk{break-inside:avoid}
th{background:#1D5D89;color:#fff;font-weight:700;padding:1.2mm 1.5mm;text-align:right}
td{border-bottom:1px solid #e3e8ec;padding:0.55mm 1.5mm;text-align:right;font-variant-numeric:tabular-nums}
th.l,td.l{text-align:left}
.two{display:grid;grid-template-columns:1fr 1fr;gap:5mm}
.note{font-size:8.5pt;color:#555}
.pb{page-break-before:always}
"""
today="2026年11月18日"
doc=f"""<!doctype html><html lang=ja><head><meta charset=utf-8><title>成豊建設 SNSレポート</title><style>{css}</style></head><body>
<h1>成豊建設 SNSレポート（Instagram・TikTok）</h1>
<div class=sub>@seihoh_kensetsu ／ {today}時点の数字（Windsor.ai から取得）。このPDFは数字を固定したもので、自動では新しくなりません。</div>
<h2>主な数字</h2>
<div class=tiles>
<div class=tile><div class=k>Instagram フォロワー</div><div class=v>{IG_FOLLOWERS}</div><div class=n>人</div></div>
<div class=tile><div class=k>Instagram 総再生</div><div class=v>{F(ig_total)}</div><div class=n>投稿{len(IG)}本の合計／リールの中央値 {F(int(ig_med))}回</div></div>
<div class=tile><div class=k>TikTok フォロワー</div><div class=v>{TT_FOLLOWERS}</div><div class=n>人</div></div>
<div class=tile><div class=k>TikTok 総再生</div><div class=v>{F(tt_total)}</div><div class=n>動画{len(TT)}本の合計／中央値 {F(int(tt_med))}回</div></div>
<div class=tile><div class=k>Instagram 再生（直近90日）</div><div class=v>{F(ig90)}</div><div class=n>8/20〜11/17</div></div>
<div class=tile><div class=k>TikTok 再生（直近90日）</div><div class=v>{F(tt90)}</div><div class=n>8/20〜11/16</div></div>
<div class=tile><div class=k>TikTok プロフィールを見た</div><div class=v>{F(TT_PROF_90)}</div><div class=n>回（直近90日）</div></div>
<div class=tile><div class=k>TikTok リンクを押した</div><div class=v>{TT_BIO_90}</div><div class=n>回（直近90日）</div></div>
</div>
<p>いちばん見られた投稿は、Instagram が「{html.escape(top_ig[2])}」（{F(top_ig[3])}回）、TikTok が「{html.escape(top_tt[1])}」（{F(top_tt[2])}回）です。</p>
<h2>Instagram プロフィールのアクティビティ（アプリのインサイト・90日間）</h2>
<div class=tiles style="grid-template-columns:repeat(3,1fr)">
<div class=tile><div class=k>プロフィールへのアクセス</div><div class=v>{F(PROFILE_ACT[0])}</div><div class=n>回</div></div>
<div class=tile><div class=k>自己紹介リンクのタップ</div><div class=v>{PROFILE_ACT[1]}</div><div class=n>回（アクセスの約{PROFILE_ACT[1]/PROFILE_ACT[0]*100:.1f}%）</div></div>
<div class=tile><div class=k>ビジネスの住所のタップ</div><div class=v>{PROFILE_ACT[2]}</div><div class=n>回</div></div>
</div>
<div class=note>11/16 にいただいたアプリの画面から写した数字です。</div>
<div class=blk><h2>Instagram 毎日の再生（直近90日）</h2>
{bars(IG_DAILY,IG_DAILY_START,cap=25000)}
<div class=note>8/24 は {F(max(IG_DAILY))}回（グラフの上限を超えています）。</div></div>
<div class=blk><h2>TikTok 毎日の再生（直近90日）</h2>
{bars(TT_DAILY,'2026-08-20',color='#4A8BB5')}</div>
<div class="two">
<div><h2>種類ごと（Instagram リール）</h2><table><tr><th class=l>種類</th><th>本数</th><th>再生の中央値</th><th>3秒で離れた</th></tr>{rows_kind}</table><div class=note>種類は題名の言葉で分けています。</div></div>
<div><h2>投稿時間ごと（日本時間）</h2><table><tr><th>時間</th><th>IG本数</th><th>IG再生の中央値</th><th>TT本数</th><th>TT再生の中央値</th><th>TTプロフィールを見た</th></tr>{rows_hour}</table><div class=note>17時台の投稿は9〜10月に多く、同じころ中身も変わっているため、時間だけの差とは言い切れません。</div></div>
</div>
<div class="two">
<div><h2>Instagram フォロワーの年代と性別</h2><table><tr><th>年代</th><th>男性</th><th>女性</th><th>不明</th><th>合計</th></tr>{rows_age}</table></div>
<div><h2>TikTok フォロワーの年代</h2><table><tr><th>年代</th><th>割合</th></tr>{rows_ttage}</table><div class=note>性別：男性 {TT_GENDER['男性']}%・女性 {TT_GENDER['女性']}%。TikTok は割合だけを出します。</div></div>
</div>
<h2 class=pb>Instagram 全部の投稿</h2>
<table><tr><th>日付</th><th>時間</th><th class=l>題名</th><th>再生</th><th>届いた人</th><th>保存</th><th>シェア</th><th>3秒で離れた</th></tr>{rows_ig}</table>
<h2 class=pb>TikTok 全部の動画</h2>
<table><tr><th>日付</th><th>時間</th><th class=l>題名</th><th>再生</th><th>見た人</th><th>プロフィールを見た</th><th>フォローした</th><th>最後まで見た</th></tr>{rows_tt}</table>
<h2>言葉の意味</h2>
<ul class=note>
<li>再生：動画が再生された回数。同じ人が何度も見ると、その分数えます。</li>
<li>届いた人・見た人：その投稿を見た人の数（1人1回）。</li>
<li>3秒で離れた：再生が始まって3秒以内に見るのをやめた人の割合。少ないほど、最初でつかめています。</li>
<li>中央値：数字を小さい順に並べたときの真ん中の値。1本だけ大きく伸びた回に引っ張られません。</li>
<li>時間は日本時間です。</li>
</ul>
</body></html>"""
open('report.html','w').write(doc)
print('ok',ig_total,tt_total,ig90,tt90)
