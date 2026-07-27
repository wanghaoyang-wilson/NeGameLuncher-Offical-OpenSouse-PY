import enumList
import time_out
import threading
current = threading.current_thread()
SHOW_LOG = True
def print_log(text,type=enumList.enumList_log.INFO,Model=None,ChildModel=None,threadld=None):
    if type == enumList.enumList_log.DEBUG:
        text_type = "DEBUG"
    elif type == enumList.enumList_log.INFO:
        text_type = "INFO"
    elif type == enumList.enumList_log.WARN:
        text_type = "WARN"
    elif type == enumList.enumList_log.ERROR:
        text_type = "ERROR"
    elif type == enumList.enumList_log.FATAL:
        text_type = "FATAL"
    else:
        text_type = '????'
    if SHOW_LOG:
        print(f"[{time_out.returnTimeOut()}] [{text_type}] [{Model}] [{ChildModel}] [{threadld}] : {text}")

 