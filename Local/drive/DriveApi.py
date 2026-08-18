# drive_plugin_api.py
from typing import Any, Tuple, Optional, Dict, List
from pathlib import Path

import cmd_model
import enumList
from event_bus import G_event_bus
from jsonedit import ConfigManager

from drive_loding import RunDriveCore, DriveMetaData



class NeGameEngineDriveClass:
    REGISTER_NAME = "NL.Deive.DriveAPI"
    def __init__(self):
        pass
    def run(self,*argv):
        cmd_model.print_log("驱动API已启动", enumList.enumList_log.INFO, Model=enumList.enumList_model.CORE, ChildModel=enumList.enumList_Core.GAMEPMGR, threadld=None)
        cmd_model.print_log(f"arg:{argv}",enumList.enumList_log.INFO)