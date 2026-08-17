import jsonedit
import time_out
import enumList
import fileRW
import cmd_model
import event_bus
import config_mgr
code = enumList.MsgCode()
class event_core():
    def __init__(self):
        event_bus.G_event_bus.SubEvent(code.EVENT_PLAYER_CHANGE_NAME,0,self._Home_Player_name_Changed,enumList.Event_code.ALL)
    def _Home_Player_name_Changed(self,name):
        config_mgr.Pla.edit("playerCfg.name", name, overwrite=True)
        cmd_model.print_log(f'UI core is run change name {name}',enumList.enumList_log.INFO,enumList.enumList_model.ALL,'all',None)
    def Home_Player_Name_get(self):
        return config_mgr.Pla.get("playerCfg.name")
event_core = event_core()