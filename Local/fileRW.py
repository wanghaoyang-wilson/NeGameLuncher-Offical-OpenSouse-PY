def RFTxtLine(file_OJ,Index):
    try:
        file_OJ.seek(0)
        lines = file_OJ.readlines()
        if 0 <= Index < len(lines):
            return lines[Index].strip()
    except Exception:
        pass
    return ''