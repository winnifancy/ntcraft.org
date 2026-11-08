"""修正失效的圖片連結：消息或網頁裡寫 xxx.png / xxx.jpg，但檔案已被自動轉成 xxx.webp 時，
把連結改成 .webp。用來處理「先上傳圖片、幾秒後才存消息」造成的時間差。"""
import os, re

REF = re.compile(r'(/?assets/images/[^\s"\')]+?)\.(png|jpe?g)\b', re.I)
fixed = 0
targets = []
for root, _, files in os.walk('.'):
    if root.startswith(('./.git', './assets', './_site', './node_modules', './vendor')):
        continue
    targets += [os.path.join(root, f) for f in files if f.endswith(('.md', '.html', '.yml'))]
for fp in targets:
    t = open(fp, encoding='utf-8').read()
    def repl(m):
        global fixed
        stem = m.group(1)
        local = stem.lstrip('/')
        if not os.path.exists(f'{local}.{m.group(2)}') and os.path.exists(f'{local}.webp'):
            fixed += 1
            return f'{stem}.webp'
        return m.group(0)
    n = REF.sub(repl, t)
    if n != t:
        open(fp, 'w', encoding='utf-8').write(n)
        print(f'  fixed image link in {fp}')
print(f'fixed {fixed} link(s)')
