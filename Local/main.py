from UI import *
import cmd_model
import enumList
import fileRW
import res_text
import config_mgr
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
def main(argv = None):
    file_init()
    app = QApplication(sys.argv)
    cursor_png = QPixmap("Local/img/mouse.png")
    main_cursor = QCursor(cursor_png,0,0)
    app.setOverrideCursor(main_cursor)
    win = LuncherUI()
    win.show()
    sys.exit(app.exec())
main(sys.argv)