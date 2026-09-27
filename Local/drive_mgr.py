import drive_loding
import cmd_model
import enumList

_drive_core = drive_loding.RunDriveCore()


def start():
    _drive_core.on_error = lambda filename, err: cmd_model.print_log(
        f"驱动[{filename}]异常:{str(err)}",
        enumList.enumList_log.ERROR,
        Model=enumList.enumList_model.CORE,
        ChildModel=enumList.enumList_Core.GAMEPMGR,
        threadld=None,
    )
    _drive_core.init()


# ===================== 注入型 Drive API =====================
def inject(key: str, value):
    """【API】向所有驱动注入一条关键信息（可覆盖）。"""
    return _drive_core.inject(key, value)


def get_inject(key: str, default=None):
    """【API】读取已注入的关键信息。"""
    return _drive_core.get_inject(key, default)


def inject_context(**kwargs):
    """【API】批量注入关键信息：inject_context(player="X", theme="NL.Theme.Dark")"""
    return _drive_core.inject_context(**kwargs)


def get_all_injects():
    """【API】导出全部已注入信息。"""
    return _drive_core.get_all_injects()


def get_core():
    """【API】拿到驱动核心 RunDriveCore（用于调用更底层 API）。"""
    return _drive_core


def get_drive_instance(mod_name: str):
    """【API】按模块名获取驱动实例。"""
    return _drive_core.get_drive_instance(mod_name)


def run_drive_api(mod_name: str, method_name: str, *args, **kwargs):
    try:
        return _drive_core.call_drive_method(mod_name, method_name, *args, **kwargs)
    except Exception as e:
        cmd_model.print_log(
            f"调用驱动[{mod_name}.{method_name}]异常:{str(e)}",
            enumList.enumList_log.ERROR,
            Model=enumList.enumList_model.CORE,
            ChildModel=enumList.enumList_Core.GAMEPMGR,
            threadld=None,
        )
        return _drive_core.call_drive_method_safe(mod_name, method_name, *args, **kwargs)


def run_drive_api_safe(mod_name: str, method_name: str, *args, **kwargs):
    try:
        return _drive_core.call_drive_method_safe(mod_name, method_name, *args, **kwargs)
    except Exception as e:
        cmd_model.print_log(
            f"调用驱动[{mod_name}.{method_name}]异常:{str(e)}",
            enumList.enumList_log.ERROR,
            Model=enumList.enumList_model.CORE,
            ChildModel=enumList.enumList_Core.GAMEPMGR,
            threadld=None,
        )
        return None
