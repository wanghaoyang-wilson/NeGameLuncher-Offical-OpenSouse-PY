import enumList

# =====================================================================
# EMCC：事件名 <-> 事件码 的统一翻译层
# 原实现是手写 if/elif 硬编码，极易与 enumList.MsgCode 不同步，
# 一旦漏写/写错（例如 EVENT_PLAYER_INFO 被写成 VENT_PLAYER_INFO），
# 事件名映射错误会直接抛 KeyError 导致引擎崩溃。
# 现改为：从 enumList.MsgCode 自动派生「数值 -> 名称」反向映射，
# 名字永远与枚举表同步，新增事件无需改这里。
# =====================================================================

_NAME_MAP = {}
for _attr in dir(enumList.MsgCode):
    if _attr.isupper():
        _val = getattr(enumList.MsgCode, _attr)
        if isinstance(_val, int) and _val not in _NAME_MAP:
            _NAME_MAP[_val] = _attr


def look(code):
    """返回事件码对应的名称；未注册时返回 None（不抛错，避免引擎崩溃）。"""
    return _NAME_MAP.get(code)


class Event_code:
    CORE = 0
    UI = 1
    NETWORK = 2
    AUTH = 3
    LOGGER = 4
    ALL = 5


EC = Event_code()
Ei = enumList.MsgCode()

# 事件 -> 分组 归属表（沿用原有配置）
group = {
    Ei.EVENT_GAME_START: EC.CORE,
    Ei.EVENT_GAME_STOP: EC.CORE,
    Ei.EVENT_GAME_CHANGE: EC.UI,
    Ei.EVENT_GAME_SETTING: EC.UI,
    Ei.EVENT_PLAYER_SETTING: EC.CORE,
    Ei.EVENT_PLAYER_INFO: EC.UI,
    Ei.EVENT_PLAYER_CHANGE_NAME: EC.CORE,
    Ei.EVENT_PLAYER_RUN_OFFLINE: EC.AUTH,
    Ei.EVENT_REPO_CHILCK_GAME: EC.CORE,
    Ei.EVENT_REPO_CHANGE_GAME: EC.UI,
}
