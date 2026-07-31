def look(code):
    if code == 0:
            return "EVENT_GAME_START"
class Event_code:
    CORE = 0
    UI = 1
    NETWORK = 2
    AUH = 3
    LOGGER = 4
    ALL = 5
import enumList
EC = Event_code()
Ei = enumList.MsgCode()
group = {
      Ei.EVENT_GAME_START : f"{EC.UI}"
}