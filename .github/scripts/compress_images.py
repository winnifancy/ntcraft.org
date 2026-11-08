"""自動壓縮網站圖片：寬或高超過 1600px、或檔案超過 600KB 的圖片，
會轉正方向、縮到最長邊 1600px、移除 GPS 等相機資訊，並以相同檔名存回。
用法：python compress_images.py 檔案1 檔案2 ..."""
import os, sys
from PIL import Image, ImageOps

MAX_SIDE = 1600
MAX_BYTES = 600 * 1024
changed = []
for path in sys.argv[1:]:
    ext = os.path.splitext(path)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.webp') or not os.path.isfile(path):
        continue
    before = os.path.getsize(path)
    with Image.open(path) as im:
        if max(im.size) <= MAX_SIDE and before <= MAX_BYTES:
            continue
        im = ImageOps.exif_transpose(im)
        im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
        if ext in ('.jpg', '.jpeg'):
            im.convert('RGB').save(path, 'JPEG', quality=80, optimize=True, progressive=True)
        elif ext == '.webp':
            im.save(path, 'WEBP', quality=80, method=6)
        else:
            im.save(path, 'PNG', optimize=True)
    after = os.path.getsize(path)
    if ext == '.png' and after > MAX_BYTES:
        # PNG 照片壓不小 → 轉成 WebP，並更新消息與網頁裡的圖片連結
        new = os.path.splitext(path)[0] + '.webp'
        with Image.open(path) as im2:
            im2.save(new, 'WEBP', quality=82, method=6)
        os.remove(path)
        old_ref, new_ref = '/' + path.lstrip('./'), '/' + new.lstrip('./')
        for root, _, files in os.walk('.'):
            if root.startswith(('./.git', './assets', './_site')): continue
            for fn in files:
                if fn.endswith(('.md', '.html', '.yml')):
                    fp = os.path.join(root, fn)
                    t = open(fp, encoding='utf-8').read()
                    if old_ref in t or old_ref.lstrip('/') in t:
                        open(fp, 'w', encoding='utf-8').write(t.replace(old_ref, new_ref).replace(old_ref.lstrip('/'), new_ref.lstrip('/')))
                        print(f'  updated link in {fp}')
        print(f'{path}: {before//1024} KB -> {new} {os.path.getsize(new)//1024} KB')
        path = new
    else:
        print(f'{path}: {before//1024} KB -> {after//1024} KB')
    changed.append(path)
print(f'compressed {len(changed)} file(s)')
