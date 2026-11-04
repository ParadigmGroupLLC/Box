# 引き継ぎ：Windsor.ai で年齢のデータが取れるか確かめる（2026-11-04）

新しいセッションで、この作業の続きをするためのメモです。返事と報告は、常に日本語で書きます。

## やること
1. Windsor.ai のツール（get_connectors・get_fields・get_accounts・get_data）が使えるか確かめる。
2. TikTok（オーガニック）で、次の2つが取れるか確かめる。
   - アカウント全体のフォロワーの年齢
   - 動画ごとの視聴者の年齢
3. Instagram でも、投稿ごとの視聴者の年齢が取れるか確かめる。
4. 取れたら、SNS分析のダッシュボードに足す。
   - ダッシュボード：https://claude.ai/artifact/65VoMh9C6AF78X1tH3uFWQ
   - 足す場所：「見ている人」の TikTok の年齢（今は「取れません」）と、発見4（若手が主役の投稿）の表

## わかっていること
- Supermetrics では、どちらの年齢も取れない（TikTok は性別と国だけ。Instagram はフォロワー全体の年齢だけ）。
- Supermetrics の Instagram の接続は、2026-11-03 に切れていた。つなぎ直しが必要。
- 対象のアカウント：@seihoh_kensetsu（成豊建設）
  - Instagram：アカウントID 17841448027926690
  - TikTok：@seihoh_kensetsu
- オフィスのページ：https://claude.ai/artifact/9ZxnEsfxZnDXq2Xwmcf5N1
  - コメントの通知を受けるには、新しいセッションでもう一度「見守り（watch）」を登録する。
- Instagram と TikTok を自動で開いたり読み取ったりはしない（利用規約のため）。

## 関係するファイル
- 成豊建設/分析/2026-11-03_若い人に見られている投稿.md
- 成豊建設/分析/2026-11-02_アカウント分析.md
- 成豊建設/分析/2026-11-02_TikTok分析.md
