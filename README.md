# Box：こもれびコーヒーのリール制作

Claude Code のサブエージェント10人で、リールを作るためのフォルダです。映像は [HyperFrames](https://hyperframes.heygen.com)（HTMLで書いて MP4 に書き出す道具）で作ります。

## 中身
| 場所 | 中身 |
|---|---|
| `CLAUDE.md` | 全員が守る共通ルール（アカウント・口調・デザイン・音・書き出し） |
| `.claude/agents/` | 10人分のエージェント（統括は `reel-producer`） |
| `.claude/skills/` | HyperFrames の使い方（映像担当が読む） |
| `テンプレート/` | 縦 1080×1920 の HyperFrames プロジェクトのひな形。N本目/project/ にコピーして使う |
| `ネタ帳/` | リサーチ対象・使用済みの投稿・リサーチ結果 |
| `効果音/` | 使ってよい効果音だけを入れる |

## 準備
Node.js 22 以上と FFmpeg が必要です。

```bash
npm install
npm run browser
npm run doctor
```

## 使い方
Claude Code で `reel-producer` に「ネタを出して」「N本目を編集して」などと頼みます。

テンプレートを単体で書き出すとき：

```bash
cd テンプレート
npx hyperframes render -o out.mp4
```
