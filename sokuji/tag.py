def to_tag(name: str) -> str:
    if name == '東工大マリオカートサークル':
        return 'TT'
    elif name == 'ハラスメント -HαM-':
        return 'HαM'
    for word in ['team', 'mk']:
        if not word in name.lower():
            break
        names = list(name.split())
        if len(names) == 1:
            break
        names = [n for n in names if not word in n.lower()]
        if len(names) == 1 or word == 'mk':
            name = names[0]
            break
        if names:
            name = ' '.join(names)
    for d in {'チーム','スクアッド','💎','*','私立','幼稚園','_MK8DX'}:
        name = name.replace(d, '')
    for s in {'の',"'s",'(','（',' ','..'}:
        if name.split(s)[0] != '':
            name = name.split(s)[0]
    return name
