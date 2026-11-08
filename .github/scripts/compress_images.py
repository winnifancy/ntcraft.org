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
    changed.append(path)
    print(f'{path}: {before//1024} KB -> {after//1024} KB')
print(f'compressed {len(changed)} file(s)')
