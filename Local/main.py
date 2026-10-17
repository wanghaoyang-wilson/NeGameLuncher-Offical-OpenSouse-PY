from UI import *
import cmd_model
import enumList
import fileRW
import res_text
import config_mgr
import os_infomation
import drive_mgr
def file_init():
    List = fileRW.create_project_flat_directories("NeGameLauncher", "config", "cache", "log")
    enumList.CFGDIRROOT = List[1]
    enumList.CATHDIRROOT = List[2]
    enumList.LOGDIRROOT = List[3]
    enumList.NECFGROOT = List[0]
    cmd_model.print_log(f"CFGDIRROOT: {enumList.CFGDIRROOT}",enumList.enumList_log.INFO,Model=enumList.enumList_model.CORE,ChildModel=enumList.enumList_Core.GAMEPMGR,threadld=None)
    cmd_model.print_log(f"CATHDIRROOT: {enumList.CATHDIRROOT}",enumList.enumList_log.INFO,Model=enumList.enumList_model.CORE,ChildModel=enumList.enumList_Core.GAMEPMGR,threadld=None)
    cmd_model.print_log(f"LOGDIRROOT: {enumList.LOGDIRROOT}",enumList.enumList_log.INFO,Model=enumList.enumList_model.CORE,ChildModel=enumList.enumList_Core.GAMEPMGR,threadld=None)
    cmd_model.print_log(f"NECFGROOT: {enumList.NECFGROOT}",enumList.enumList_log.INFO,Model=enumList.enumList_model.CORE,ChildModel=enumList.enumList_Core.GAMEPMGR,threadld=None)
    fileRW.create_file(f"{enumList.CFGDIRROOT}/version.json"), ""
    config_mgr.CfgJsonRun()
    config_mgr.init_cfg()
    fileRW.create_file(f"{enumList.LOGDIRROOT}/log.txt","")
    # 注入型 Drive API：向所有驱动注入各种关键信息（示例）
    drive_mgr.inject_context(
        version=enumList.VERSION_INFO,
        player_name=config_mgr.Pla.get("playerCfg.name"),
        theme=enumList.theme.DARK,
        event_bus=__import__("event_bus", fromlist=["G_event_bus"]).G_event_bus,
    )
    drive_mgr.start()
def main(argv = None):
    file_init()
    """cmd_model.print_log_noInfo("====================配置信息=====================")
    cmd_model.print_log_noInfo(str(os_infomation.get_system_and_env_info(mode="get",python_fetch_pip_packages=False,timeout=3.0)))
    cmd_model.print_log_noInfo("================================================")"""
    cmd_model.print_log(f"argv: {argv}",enumList.enumList_log.INFO,Model=enumList.enumList_model.CORE,ChildModel=enumList.enumList_Core.GAMEPMGR,threadld=None)
    app = QApplication(sys.argv)
    if not config_mgr.Ndb.get("NoChangeMouseStyle"):
        cursor_png = QPixmap("Local/img/mouse.png")
        main_cursor = QCursor(cursor_png,0,0)
        app.setOverrideCursor(main_cursor)
    if "--debug" in argv:
        if not config_mgr.Ndb.get("DebugNoMessage"):
            QMessageBox.warning(None, "Debug Mode", "Debug mode is enabled. This may affect performance and stability.", QMessageBox.Ok)
        config_mgr.Ndb.edit("isDebug", True, overwrite=True)
        cmd_model.print_log(f"Debug mode enabled",enumList.enumList_log.INFO,Model=enumList.enumList_model.CORE,ChildModel=enumList.enumList_Core.GAMEPMGR,threadld=None)
        if not config_mgr.Ndb.get("NoRunDebugServer"):
            cmd_model.print_log(f"Starting debug server",enumList.enumList_log.INFO,Model=enumList.enumList_model.CORE,ChildModel=enumList.enumList_Core.GAMEPMGR,threadld=None)
            os.system(f"python 'Local/DebugSever/app.py' {config_mgr.Ndb.get('DebugHost')} {config_mgr.Ndb.get('DebugServerPort')} &")
            cmd_model.print_log(f"Debug server started",enumList.enumList_log.INFO,Model=enumList.enumList_model.CORE,ChildModel=enumList.enumList_Core.GAMEPMGR,threadld=None)
    win = LuncherUI(args=argv)
    win.show()
    if config_mgr.Pla.get("playerCfg.setting.isDarkMode"):
        win.switch_theme(enumList.theme.DARK)
    else:
        win.switch_theme(enumList.theme.LIGHT)  
    sys.exit(app.exec())
