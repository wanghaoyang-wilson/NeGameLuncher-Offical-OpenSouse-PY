<<<<<<< HEAD
def RFTxtLine(file_OJ,Index):
    try:
        file_OJ.seek(0)
        lines = file_OJ.readlines()
        if 0 <= Index < len(lines):
            return lines[Index].strip()
    except Exception:
        pass
=======
def RFTxtLine(file_OJ,Index):
    try:
        file_OJ.seek(0)
        lines = file_OJ.readlines()
        if 0 <= Index < len(lines):
            return lines[Index].strip()
    except Exception:
        pass
>>>>>>> 31773b821b215859d6f47236e15a589ce8c55fb0
    return ''