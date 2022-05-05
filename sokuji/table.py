from io import BytesIO
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont, ImageChops
from discord import File


BOLD_L = ImageFont.truetype('fonts/NotoSansCJKjp-Bold.otf', size=250)
BOLD_S = ImageFont.truetype('fonts/NotoSansCJKjp-Bold.otf', size=100)
THIN = ImageFont.truetype('fonts/NotoSansCJKjp-Thin.otf', size=50)
FIRST = Image.open('images/first.png')
SECOND = Image.open('images/second.png')


def make_pltimg6(scores: list[list[int]]) -> Image:
    difs = list(map(lambda s: s[0]-s[1], scores))
    min_dif = min(difs)
    max_dif = max(difs)
    if min_dif < 0 and max_dif > 0 and max(max_dif, -min_dif) // min(max_dif, -min_dif) < 3:
        y = [min_dif, 0, max_dif]
    else:
        y = [min_dif, (min_dif+max_dif)//2, max_dif]

    fig = plt.figure(figsize=(12.8, 3), facecolor='#2c3e50', tight_layout=False)
    ax = fig.add_subplot(111, xmargin=0, facecolor='#2c3e50')
    ax.set_xticks([])
    ax.set_yticks(y)
    ax.set_yticklabels(y, fontsize=20)
    ax.grid(axis='y', color='#95a5a6')
    if min_dif <= 0 and max_dif >= 0:
        ax.plot([0]*len(difs), color='#bdc3c7')
    ax.plot(difs, color='#c0392b',linewidth=4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='y', colors='#7f8c8d')
    ax.tick_params(color='#2c3e50')
    binary = BytesIO()
    fig.savefig(binary, format='png')
    binary.seek(0)
    return Image.open(binary)


def add_margin(img: Image, top=0, right=0, bottom=0, left=0, color='#2c3e50') -> Image:
    width, height = img.size
    new_width = width + right + left
    new_height = height + top + bottom
    new = Image.new(img.mode, (new_width, new_height), color)
    new.paste(img, (left, top))
    return new


def trimH(img: Image, color):
    bg = Image.new(mode="RGB", size=img.size, color=color)
    diff = ImageChops.difference(img, bg)
    croprange = diff.convert("RGB").getbbox()
    return img.crop((croprange[0],0,croprange[2],img.height))


def make_tagimg6(tag: str) -> Image:
    img = Image.new(mode='RGB', size=(2000,300), color='#2c3e50')
    draw = ImageDraw.Draw(img)
    draw.text((0,125), tag, fill='#3498db', font=BOLD_L, anchor='lm')
    img = trimH(img,'#2c3e50')
    if img.width > 500:
        img = img.resize((500,img.height))
    return img


def make_img6(tags: list[str], scores: list[list[int]]) -> Image:
    img = add_margin(make_pltimg6(scores), top=420)
    img.paste(make_tagimg6(tags[0]), (110, 155))
    tagimg = make_tagimg6(tags[1])
    img.paste(tagimg, (1170-tagimg.width, 155))

    if scores[-1][0] > scores[-1][1]:
        rank1 = FIRST
        rank2 = SECOND
    elif scores[-1][0] < scores[-1][1]:
        rank1 = SECOND
        rank2 = FIRST
    else:
        rank1 = FIRST
        rank2 = FIRST
    img.paste(rank1,(120,40),rank1)
    img.paste(rank2,(1032,40),rank2)

    draw = ImageDraw.Draw(img)
    draw.text((640,50), f'{scores[-1][0]} - {scores[-1][1]}', fill='#3498db', font=BOLD_S, anchor='ma')
    draw.text((640,85), '({:+})'.format(scores[-1][0]-scores[-1][1]), fill='#3498db', font=THIN, anchor='mb')
    return img


def make(tags: list[str], scores: list[list[int]]) -> File:
    binary = BytesIO()
    if len(tags) == 2:
        make_img6(tags, scores).save(binary, 'png')
    binary.seek(0)
    file = File(fp=binary, filename='table.png', description=' '.join(tags))
    binary.close()
    return file
