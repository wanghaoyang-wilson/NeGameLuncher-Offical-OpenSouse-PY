def look(code):
    if code == 0:
         return "EVENT_GAME_START"
    elif code == 1:
         return "EVENT_GAME_STOP"
    elif code == 2:
         return "EVENT_GAME_CHANGE"
    elif code == 3:
         return "EVENT_GAME_SETTING"
    elif code == 4:
         return "EVENT_PLAYER_SETTING"
    elif code == 5:
         return "VENT_PLAYER_INFO"
    elif code == 6:
         return "EVENT_PLAYER_CHANGE_NAME"
    elif code == 7:
         return "EVENT_PLAYER_RUN_OFFLINE"
    elif code == 8:
         return "EVENT_REPO_CHILCK_GAME"
    elif code == 9:
         return "EVENT_REPO_CHANGE_GAME"
class Event_code:
    CORE = 0
    UI = 1
    NETWORK = 2
    AUTH = 3
    LOGGER = 4
    ALL = 5
import enumList
EC = Event_code()
Ei = enumList.MsgCode()
group = {
      Ei.EVENT_GAME_START : EC.CORE,
      Ei.EVENT_GAME_STOP  : EC.CORE,
      Ei.EVENT_GAME_CHANGE: EC.UI,
      Ei.EVENT_GAME_SETTING:EC.UI,
      Ei.EVENT_PLAYER_SETTING:EC.CORE,
      Ei.EVENT_PLAYER_INFO:EC.UI,
      Ei.EVENT_PLAYER_CHANGE_NAME : EC.CORE,
      Ei.EVENT_PLAYER_RUN_OFFLINE : EC.AUTH,
      Ei.EVENT_REPO_CHILCK_GAME : EC.CORE,
      Ei.EVENT_REPO_CHANGE_GAME : EC.UI
}