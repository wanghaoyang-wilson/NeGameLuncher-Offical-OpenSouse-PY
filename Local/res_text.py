def sk(theme):
    if theme == 'NL.Theme.Dark':
        with open(r"Local\dark.qss",'r',encoding='utf-8') as f:
            qss = f.read()
    return qss