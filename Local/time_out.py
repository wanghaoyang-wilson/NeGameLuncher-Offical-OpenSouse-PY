<<<<<<< HEAD
from datetime import datetime
import time

def returnTimeOut():
    now = datetime.utcnow()
    ms = now.microsecond // 1000
=======
from datetime import datetime
import time

def returnTimeOut():
    now = datetime.utcnow()
    ms = now.microsecond // 1000
>>>>>>> 31773b821b215859d6f47236e15a589ce8c55fb0
    return f"{now.year}:{now.month:02d}:{now.day:02d}:{now.hour:02d}:{now.minute:02d}:{now.second:02d}:{ms:03d}"