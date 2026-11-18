# 成豊建設 クライアント向けレポート（数字を固定したPDF）

- 2026-11-18 版：https://drive.google.com/file/d/1ut2t5NM3O8DXRWYP3UfOCkseXurUC7T0/view （リンクを知っている人は誰でも見られる）
- 作り方：Windsor.ai の数字を data.py に入れ、`python3 build.py` で report.html を作り、Chromium（playwright）で A4 の PDF にする。
- 中身：主な数字、プロフィールのアクティビティ（アプリの画面から手入力）、毎日の再生（Instagram・TikTok）、種類ごと、投稿時間ごと、フォロワーの年代、全部の投稿・動画の表、言葉の意味。
- 自動では新しくならない。作り直すときは data.py の数字を入れ替える。
