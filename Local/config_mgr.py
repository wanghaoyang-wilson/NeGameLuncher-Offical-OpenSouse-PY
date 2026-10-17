import enumList
import jsonedit
import time_out
from pathlib import Path
import cmd_model
def CfgJsonRun():
    global Cfg, Pla, Ndb
    Cfg = jsonedit.ConfigManager(Path(f"{enumList.CFGDIRROOT}/version.json"))
    Pla = jsonedit.ConfigManager(Path(f"{enumList.CFGDIRROOT}/player.json"))
    Ndb = jsonedit.ConfigManager(Path(f"{enumList.CFGDIRROOT}/debug.json"))
def init_cfg():
    Cfg.open(default_template={})
    Cfg.edit("versionCfg.version", enumList.VERSION_INFO,overwrite=False)
    Cfg.edit("versionCfg.versionCode", enumList.VESION_CODE,overwrite=False)
    Cfg.edit("versionCfg.time",time_out.returnTimeOut() ,overwrite=False)
    Cfg.edit("versionCfg.title", "Ne启动器",overwrite=False)
    cmd_model.print_log(f"配置初始化已写入 {enumList.CFGDIRROOT}/version.json","Logmodel.type.debug")
    Pla.open(default_template={})
    Pla.edit("playerCfg.name", "Player1", overwrite=False)
    Pla.edit("playerCfg.isOffline", True, overwrite=False)
    Pla.edit("playerCfg.isAutoLogin", False, overwrite=False)
    Pla.edit("playerCfg.setting","{}", overwrite=False)
    Pla.edit("playerCfg.setting.isDarkMode", True, overwrite=False)
    cmd_model.print_log(f"配置初始化已写入 {enumList.CFGDIRROOT}/player.json","Logmodel.type.debug")
    Ndb.open(default_template={})
    Ndb.edit("isDebug", False, overwrite=False)
    Ndb.edit("IsDisabledQss", False, overwrite=False)
    Ndb.edit("AutoStopNdb", True, overwrite=False)
    Ndb.edit("DebugHost","127.0.0.1", overwrite=False)
    Ndb.edit("DebugNoMessage", False, overwrite=False)
    Ndb.edit("NoRunDebugServer",True,overwrite=False)
    Ndb.edit("DebugServerPort",11111,overwrite=False)
    Ndb.edit("NoChangeMouseStyle",False,overwrite=False)
    cmd_model.print_log(f"配置初始化已写入 {enumList.CFGDIRROOT}/debug.json","Logmodel.type.debug")