import enumList
import jsonedit
import time_out
from pathlib import Path
import cmd_model
def CfgJsonRun():
    global Cfg, Pla
    Cfg = jsonedit.ConfigManager(Path(f"{enumList.CFGDIRROOT}/version.json"))
    Pla = jsonedit.ConfigManager(Path(f"{enumList.CFGDIRROOT}/player.json"))
def init_cfg():
    Cfg.open(default_template={})
    Cfg.edit("versionCfg.version", enumList.VERSION_INFO,overwrite=False)
    Cfg.edit("versionCfg.versionCode", enumList.VESION_CODE,overwrite=False)
    Cfg.edit("versionCfg.time",time_out.returnTimeOut() ,overwrite=True)
    cmd_model.print_log(f"配置初始化已写入 {enumList.CFGDIRROOT}/version.json","Logmodel.type.debug")
    Pla.open(default_template={})
    Pla.edit("playerCfg.name", "Player1", overwrite=False)
    Pla.edit("playerCfg.isOffline", True, overwrite=False)
    Pla.edit("playerCfg.isDarkMode", True, overwrite=False)
    Pla.edit("playerCfg.isAutoLogin", False, overwrite=False)
    cmd_model.print_log(f"配置初始化已写入 {enumList.CFGDIRROOT}/player.json","Logmodel.type.debug")
