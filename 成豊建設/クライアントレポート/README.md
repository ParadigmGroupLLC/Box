# 成豊建設 クライアント向けレポート（数字を固定したPDF）

- 最新（2026-11-18 第3版）：https://drive.google.com/file/d/1yWnHJshnDbQaZl_WxO5ZHsljn2D66wfe/view （リンクを知っている人は誰でも見られる）
  - 主な数字を Instagram・TikTok の比べる表に。毎日の再生のグラフを外し、フォロワーの多い市区町村（日本語）を追加。
- 第2版（TikTok のプロフィールの数字入り）：https://drive.google.com/file/d/1qlI5f3b3xtxEPG4F3W2zV922LAiqor7A/view （ドライブでの名前は「（旧2）…」）
- 最初の版（TikTok なし）：https://drive.google.com/file/d/1ut2t5NM3O8DXRWYP3UfOCkseXurUC7T0/view （ドライブでの名前は「（旧）…」）
- 作り方：Windsor.ai の数字を data.py に入れ、`python3 build.py` で report.html を作り、Chromium（playwright）で A4 の PDF にする。
- 中身：主な数字（Instagram・TikTok の比べる表）、プロフィールのアクティビティ（Instagram はアプリの画面から手入力・TikTok は Windsor.ai）、種類ごと、投稿時間ごと、フォロワーの年代、フォロワーの多い市区町村、全部の投稿・動画の表、言葉の意味。
- 自動では新しくならない。作り直すときは data.py の数字を入れ替える。
