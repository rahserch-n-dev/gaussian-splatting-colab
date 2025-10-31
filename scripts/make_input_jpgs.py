from PIL import Image
import os

src = 'scenes/6th-Forrest/images'
dst = 'scenes/6th-Forrest/input'
os.makedirs(dst, exist_ok=True)

files = sorted([f for f in os.listdir(src) if f.lower().endswith('.jpg')])
print('Found', len(files), 'jpg files')
for i,f in enumerate(files,1):
    p = os.path.join(src,f)
    img = Image.open(p)
    img.thumbnail((1600,1600))
    outp = os.path.join(dst,f)
    img.save(outp, 'JPEG', quality=90)
    if i%50==0:
        print('Processed',i)
print('Done')
