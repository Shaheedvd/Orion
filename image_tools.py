from PIL import Image
import os

def make_thumbnail(path, size=(256,256)):
    im = Image.open(path)
    im.thumbnail(size)
    base, ext = os.path.splitext(path)
    out = base + '.thumb' + ext
    im.save(out)
    return out
