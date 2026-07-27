from datetime import datetime
import time

def returnTimeOut():
    now = datetime.utcnow()
    ms = now.microsecond // 1000
    return f"{now.year}:{now.month:02d}:{now.day:02d}:{now.hour:02d}:{now.minute:02d}:{now.second:02d}:{ms:03d}"