import drive_loding
import cmd_model
import enumList
_drive_core = drive_loding.RunDriveCore()
def start():
    _drive_core.on_error = lambda filename, err: cmd_model.print_log(f"驱动[{filename}]异常:{str(err)}",enumList.enumList_log.ERROR,Model=enumList.enumList_model.CORE,ChildModel=enumList.enumList_Core.GAMEPMGR,threadld=None)
    _drive_core.init()
def run_drive_api(mod_name: str, method_name: str, *args, **kwargs):
    try:
        return _drive_core.call_drive_method(mod_name, method_name, *args, **kwargs)
    except Exception as e:
        cmd_model.print_log(f"调用驱动[{mod_name}.{method_name}]异常:{str(e)}", enumList.enumList_log.ERROR, Model=enumList.enumList_model.CORE, ChildModel=enumList.enumList_Core.GAMEPMGR, threadld=None)
        return _drive_core.call_drive_method_safe(mod_name, method_name, *args, **kwargs)
def run_drive_api_safe(mod_name: str, method_name: str, *args, **kwargs):
    try:
        return _drive_core.call_drive_method_safe(mod_name, method_name, *args, **kwargs)
    except Exception as e:
        cmd_model.print_log(f"调用驱动[{mod_name}.{method_name}]异常:{str(e)}", enumList.enumList_log.ERROR, Model=enumList.enumList_model.CORE, ChildModel=enumList.enumList_Core.GAMEPMGR, threadld=None)
        return None