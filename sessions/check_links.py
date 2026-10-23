#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量验证 timeline.html 里所有外链（wiki/site/img 本地文件）。
用法: python3 check_links.py [--net]
  --net  联网验证 HTTP 状态（需代理时自行设置 ALL_PROXY 环境变量）
不加 --net 只做本地检查：链接格式、img 文件存在性。"""
import io, os, re, sys, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "timeline.html")
NET = "--net" in sys.argv

s = io.open(HTML, encoding="utf-8").read()
urls = sorted(set(re.findall(r'(?:wiki|site):"([^"]+)"', s)))

def head(url):
    env = dict(os.environ)
    p = env.get("ALL_PROXY") or env.get("https_proxy")
    cmd = ["curl", "-m", "15", "-sL", "-o", "/dev/null", "-w", "%{http_code}", "-A", "Mozilla/5.0", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20, env=env)
        return r.stdout.strip() or "???"
    except Exception as e:
        return "ERR"

bad = 0
print(f"共 {len(urls)} 个外链")
for u in urls:
    if not u.startswith("http"):
        print(f"[格式] {u}"); bad += 1; continue
    if NET:
        code = head(u)
        ok = code in ("200", "301", "302", "405", "308")
        mark = "OK " if ok else "!! "
        if not ok: bad += 1
        print(f"[{mark}{code}] {u}")

s_data = ""
DATAJS = os.path.join(HERE, "timeline-data.js")
if os.path.exists(DATAJS):
    s_data = io.open(DATAJS, encoding="utf-8").read()
    print(f"\n[数据文件 timeline-data.js: {len(s_data.splitlines())} 行]")
imgs = sorted(set(re.findall(r'img:"([^"]+)"', s + s_data)))
print(f"\n共 {len(imgs)} 张本地图片")
for i in imgs:
    p = os.path.join(HERE, i)
    if os.path.exists(p) and os.path.getsize(p) > 500:
        print(f"[OK   ] {i} ({os.path.getsize(p)//1024}KB)")
    else:
        print(f"[!!   ] {i} 缺失或过小"); bad += 1

# ===== JS 静态检查 =====
print("\nJS 结构检查")
# 1) 双逗号 / 稀疏数组（含跨行注释间隔）
sparse = re.findall(r'\][^,]*,,|,,|,\s*(?://[^\n]*)?\s*,(?=\s*[{[]|\s*\])', s)
# 精确一点：直接找 ',,' 和 ', \n ,' 模式
sparse2 = re.findall(r',\s*(?://[^\n]*)?\s*,'.replace(r'\n', r'\s'), s)
hits = sorted(set(re.findall(r',\s*(?://[^\n]*)?\s*,', s)))
if hits:
    for h in hits: print(f"[!!   ] 疑似双逗号/稀疏数组: {h!r}"); bad += 1
else:
    print("[OK   ] 无双逗号/稀疏数组")

# 1b) 数据文件里的双闭合（}},\n 形式且后面紧跟新事件才算可疑——精确匹配 '\},' 后无换行直接 '}' 的情况）
dclose = re.findall(r'\}\s*\}\s*,\s*,|"\s*\}\s*\}', s_data)
if dclose:
    for d in set(dclose): print(f"[!!   ] 疑似双闭合花括号: {d!r}"); bad += 1
else:
    print("[OK   ] 无双闭合花括号")

# 2) node 运行时模拟：提取 <script> 执行布局逻辑（若有 node）
js = re.search(r'<script>([\s\S]*)</script>', s)
if js:
    node = shutil.which("node")
    if node:
        code = '''
const s = require("fs").readFileSync(process.argv[1], "utf8");
const js = s.match(/<script>([\\s\\S]*)<\\/script>/)[1];
// 提取并 eval 所有 const XX=[...] 大数组，检查元素完整性
let bad = 0;
for (const m of js.matchAll(/const (\\w+) = (\\[[\\s\\S]*?\\n\\]);/g)) {
  try {
    const arr = eval(m[2]);
    const holes = arr.map((e,i)=>e===undefined?i:null).filter(x=>x!==null);
    if (holes.length) { console.log(`[!!   ] ${m[1]}: 稀疏/undefined 元素 @${holes}`); bad++; }
    else console.log(`[OK   ] ${m[1]}: ${arr.length} 项, 无空洞`);
  } catch(e) { console.log(`[!!   ] ${m[1]}: eval 失败 ${e.message}`); bad++; }
}
// 语法整体检查
try { new Function(js); } catch(e) { console.log("[!!   ] 语法:", e.message); bad++; }
process.exit(bad?1:0);
'''
        r = subprocess.run([node, "-e", code, HTML], capture_output=True, text=True)
        print(r.stdout.strip())
        if r.returncode: bad += 1
    else:
        print("[跳过  ] 未找到 node，跳过深度检查")
else:
    print("[!!   ] 未找到 <script> 块"); bad += 1

# 数据文件同样纳入检查（若存在）
DATAJS = os.path.join(HERE, "timeline-data.js")
if os.path.exists(DATAJS) and node:
    # 数据文件无 <script> 包裹，直接整文件检查
    code_data = '''
const js = require("fs").readFileSync(process.argv[1], "utf8");
let bad = 0;
for (const m of js.matchAll(/const (\\w+) = (\\[[\\s\\S]*?\\n\\]);/g)) {
  try {
    const arr = eval(m[2]);
    const holes = arr.map((e,i)=>e===undefined?i:null).filter(x=>x!==null);
    if (holes.length) { console.log(`[!!   ] ${m[1]}: 稀疏/undefined 元素 @${holes}`); bad++; }
    else console.log(`[OK   ] ${m[1]}: ${arr.length} 项, 无空洞`);
  } catch(e) { console.log(`[!!   ] ${m[1]}: eval 失败 ${e.message}`); bad++; }
}
try { new Function(js); } catch(e) { console.log("[!!   ] 语法:", e.message); bad++; }
process.exit(bad?1:0);
'''
    r2 = subprocess.run([node, "-e", code_data, DATAJS], capture_output=True, text=True)
    print("--- timeline-data.js ---")
    print(r2.stdout.strip())
    if r2.returncode: bad += 1

print(f"\n{'全部通过' if bad==0 else f'{bad} 个问题'}")
sys.exit(1 if bad else 0)
