import EMCC
class enumList_log:
    """
    此处是日志枚举类定义：
    改的人是GAY
    """
    DEBUG = "Logmodel.type.debug"
    INFO = "Logmodel.type.info"
    WARN = "Logmodel.type.warn"
    ERROR = "Logmodel.type.error"
    FATAL = "Logmodel.type.fatal"
class enumList_model:
    UI = 'NL.Frontend.UImodel'
    CORE = 'NL.Common.CORE'
    NETWORK = 'NL.Backend.NetWorkModel'
    AUTH = 'NL.Backend.authModel'
    LOGGER = 'NL.backenf.loggerModel'
    ALL = 'NL.AllModel'
class Event_code:
    CORE = 0
    UI = 1
    NETWORK = 2
    AUH = 3
    LOGGER = 4
    ALL = 5
class enumList_UI:
    UI = 'Nl.Frontend.UImodel.UI'
class enumList_Core:
    GAMEPMGR = "NL.Common.Core.Game.GameProcessManger"
class Other:
    _root = "Local"
    UIUICFG = rf"{_root}/UIcfg.uiui"
    APPICO = rf"{_root}/img/ico.ico"
    MD_FILE = rf"{_root}/info.md"
    CHINESE = r"Local/chinese.qss"
class language:
    CHINESE = "GL.language.chinese"
class theme:
    DARK = 'NL.Theme.Dark'
class MsgCode:
    EVENT_GAME_START = 0 
class MsgText:
    def change(code):
        return EMCC.look(code)
VERSION = "V1.0"
NAME = "Habor"
TYPE = "ALPHA"
VERSION_INFO = f"{VERSION} | {NAME} | {TYPE}" 