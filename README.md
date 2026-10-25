# 数据寻踪——AI解码生命 · 开场板式复用指南

五个场次（session1–5）共用同一套粉笔板式。板式在 `assets/`，各场页面只存内容。新增场次时按下面流程走，最快约 1 分钟。

## 目录结构

```
ai-decode-life/
├── assets/
│   ├── board.css    # 全部板式样式（各场共用，改一处全场生效）
│   └── board.js     # 翻页（方向键/空格/点击）+ 1280×720 自适应缩放
├── session1..5/     # 各场：index.html（37行内容）+ 场次配图（可选）
└── index.html       # 课程主页（场次列表）
```

## 新增场次流程

1. **复制模板目录**（选最像的）：
   ```sh
   cp -r session5 session6   # 无配图模板
   cp -r session3 session6   # 有配图模板
   ```
2. **编辑新场次的 `index.html`，只改四处**：
   - `<title>`：场次标题
   - `.kicker`：场次名（如「场次六 · 开场 · 先聊聊天」）
   - `.footer` 右侧：日期时间（如 `2026-11-14 13:00`）
   - 配图：
     - 有图：把图片放进该场目录，改 `<img src="文件名.png" …>`
     - 无图：把 `<img …>` 整行删掉（末格 `.c5` 纯文字自动排版）
3. **（可选）换问题**：只替换五个 `.cell` 内的文字，用 `<b>` 标重点词，不动结构。
4. **主页登记**：在根目录 `index.html` 的 `.sessions` 列表加一行链接。
5. 提交：
   ```sh
   git add -A && git commit -m "新增session6：…"
   ```

## 不用做的事

- 不写 CSS/JS：`../assets/` 相对路径在复制目录后天然正确。
- 不调字号：板式参数（23px / 行距1.55 / 内边距14×24 / gap18）按五问的文字量调好，问题长度相近不会溢出。

## 唯一检查点：溢出

格子高度自适应。若新问题文字明显更长（某格多出一两行），整板底部可能压到页脚。自查方法（headless Chrome）：

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --window-size=1280,720 \
  --dump-dom "file://$PWD/session6/index.html" | grep -c 'cell'
```

更直接的是让 AI 助手跑溢出检查（比较每格 `clientHeight >= scrollHeight`，且板底 ≤ 603）。问题太长时优先精简文字，其次再考虑调样式。

## 页面骨架速查

```html
<div class="slide active">
  <div class="kicker">场次N · 开场 · 先聊聊天</div>
  <div class="board5">
    <div class="cell"><div class="ct">一 · 标题</div>正文，<b>重点</b>。</div>
    <div class="cell">…（二）</div>
    <div class="cell">…（三）</div>
    <div class="cell">…（四）</div>
    <div class="cell c5"><div>
        <div class="ct">五 · 课前预言：下课后的你</div>
        正文</div>
      <img src="xxx.png" alt="课前预言">  <!-- 无图则删此行 -->
    </div>
  </div>
  <a class="timeline-btn" href="https://geying.site/timeline/bioinfo/" target="_blank">▶ 时间线</a>
</div>
```

其余（翻页、缩放、配色、虚线格、黄底末格）全部来自 `assets/board.css`。

## 提交与推送约定

**每次 push 前把本地未推送的提交压缩成一条**，远端历史保持一任务一提交。做法：

```sh
git reset --soft origin/main                 # 收回未推送提交，文件不变
git commit -m "本次改动的一句话概括"
git push
```

- 工作过程中可随意多次 commit 当存档；push 前统一折叠。
- 压缩后中间过程在远端不可见，如某次需要保留过程历史，push 前单独说明。

