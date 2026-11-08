"""最新消息自動填入「發文老師」：
新文章第一次存檔後，從 Pages CMS 的存檔紀錄找出發文者 Email，
對照 _data/teachers.yml 換成老師姓名，寫進 author（只填空的，不覆蓋）。
用法：python fill_author.py <before_sha> <after_sha>"""
import os, re, subprocess, sys

def git(*a):
    return subprocess.run(['git', *a], capture_output=True, text=True, check=True).stdout

def load_teachers():
    m = {}
    try:
        email = None
        for line in open('_data/teachers.yml', encoding='utf-8'):
            e = re.match(r'\s*-?\s*email:\s*(\S+)', line)
            n = re.match(r'\s*-?\s*name:\s*(.+)', line)
            if e: email = e.group(1).strip('"\'').lower()
            if n and email: m[email] = n.group(1).strip().strip('"\''); email = None
    except FileNotFoundError:
        pass
    return m

def who(path):
    """回傳 (email, name)：優先用存檔訊息裡的 by email，其次 committer、author。"""
    log = git('log', '-1', '--format=%s%x1f%ce%x1f%cn%x1f%ae%x1f%an', '--', path).strip()
    if not log: return None, None
    subj, ce, cn, ae, an = log.split('\x1f')
    m = re.search(r' by (\S+@\S+)\s*$', subj)
    if m: return m.group(1).lower(), None
    for e, n in ((ce, cn), (ae, an)):
        if e and 'noreply' not in e and not e.endswith('github.com'):
            return e.lower(), n
    return None, an or cn

def main(before, after):
    teachers = load_teachers()
    if re.fullmatch(r'0+', before) or not before:
        files = git('ls-files', '_news').split('\n')
    else:
        files = git('diff', '--name-only', '--diff-filter=AM', before, after, '--', '_news').split('\n')
    changed = 0
    for f in filter(None, files):
        if not f.endswith('.md') or not os.path.isfile(f): continue
        text = open(f, encoding='utf-8').read()
        fm = re.match(r'---\n(.*?)\n---\n', text, re.S)
        if not fm: continue
        head = fm.group(1)
        cur = re.search(r'^author:\s*(.*)$', head, re.M)
        if cur and cur.group(1).strip().strip('"\''): continue  # 已經有老師名字
        email, name = who(f)
        display = teachers.get(email or '', None) or name or (email.split('@')[0] if email else None)
        if not display: continue
        lines = f'author: "{display}"'
        if email: lines += f'\nauthor_email: "{email}"'
        head = re.sub(r'^author_email:.*\n?', '', head, flags=re.M).rstrip('\n')
        if re.search(r'^author:.*$', head, re.M):
            head2 = re.sub(r'^author:.*$', lines, head, count=1, flags=re.M)
        else:
            head2 = head + '\n' + lines
        text = text.replace(fm.group(0), f'---\n{head2}\n---\n', 1)
        open(f, 'w', encoding='utf-8').write(text)
        print(f'{f}: author = {display} ({email})')
        changed += 1
    print(f'filled {changed} file(s)')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '', sys.argv[2] if len(sys.argv) > 2 else 'HEAD')
