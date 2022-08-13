from PIL import Image
import requests
import io

def concat(im1, im2):
    if im1.height == im2.height:
        _im1 = im1
        _im2 = im2
    elif im1.height < im2.height:
        _im1 = im1.resize((int(im1.width * im2.height / im1.height), im2.height))
        _im2 = im2
    else:
        _im1 = im1
        _im2 = im2.resize((int(im2.width * im1.height / im2.height), im1.height))
    dst = Image.new('RGB', (_im1.width + _im2.width, _im1.height))
    dst.paste(_im1, (0, 0))
    dst.paste(_im2, (_im1.width, 0))
    return dst

i = 0
while True:
    url = f'https://raw.githubusercontent.com/sheat-git/mk8dx/main/cups/{i}.jpg'
    cup = Image.open(io.BytesIO(requests.get(url).content))
    _i = {4: 8, 5: 10, 6: 4, 7: 5, 8: 6, 9: 7, 10: 9}.get(i, i)
    for j in range(4):
        id = _i*4 + j + 1
        url = f'http://japan-mk.blog.jp/mk8dx.info-4/table/{id:02}.jpg'
        map = Image.open(io.BytesIO(requests.get(url).content))
        concat(cup, map).save(f'track/images/tracks/{i*4+j}.jpg')
    i += 1
