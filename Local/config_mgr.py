import enumList
import jsonedit
import time_out
from pathlib import Path
def CfgJsonRun():
    global Cfg
    Cfg = jsonedit.ConfigManager(Path(f"{enumList.CFGDIRROOT}/version.json"))
def init_cfg():
    Cfg.open(default_template={})
    Cfg.edit("versionCfg.version", enumList.VERSION_INFO,overwrite=False)
    Cfg.edit("versionCfg.versionCode", enumList.VESION_CODE,overwrite=False)
    Cfg.edit("versionCfg.time",time_out.returnTimeOut() ,overwrite=False)
    print(f"【配置初始化】已写入 {enumList.CFGDIRROOT}/version.json")
    print(Cfg.raw_data)