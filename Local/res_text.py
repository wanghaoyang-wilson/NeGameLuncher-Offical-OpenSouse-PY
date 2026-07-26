<<<<<<< HEAD
def sk(theme):
    if theme == 'NL.Theme.Dark':
        with open(r"Local\dark.qss",'r',encoding='utf-8') as f:
            qss = f.read()
=======
def sk(theme):
    if theme == 'NL.Theme.Dark':
        with open(r"Local\dark.qss",'r',encoding='utf-8') as f:
            qss = f.read()
>>>>>>> 31773b821b215859d6f47236e15a589ce8c55fb0
    return qss