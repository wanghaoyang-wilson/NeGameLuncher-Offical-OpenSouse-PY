import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from ui_local_ui import Ui_MainWindow
import cmd_model
import enumList
import fileRW
import res_text
enum_log = enumList.enumList_log()
enum_model = enumList.enumList_model()
enum_child_model_UI = enumList.enumList_UI()
class LuncherUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        cmd_model.print_log('UI core is init',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        self.ui.setupUi(self)
        cmd_model.print_log('UI core is setup',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        self.setWindowIcon(QIcon(enumList.Other.APPICO))
        cmd_model.print_log('UI core is set ico finish',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        self.setWindowTitle("Ne启动器")
        cmd_model.print_log('UI core is set window title',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        self.setPage(self.ui.stackedWidget,0)
        cmd_model.print_log('UI core load ui config',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None) 
        self.uiui = open(enumList.Other.UIUICFG,"r",encoding="utf-8")
        self.ui.Main_Login_Button.clicked.connect(self.login)
        self.ui.Main_Exit_Button.clicked.connect(self.exit)
        self.ui.Main_OffLine_Run.clicked.connect(lambda:self.setPage(self.ui.stackedWidget,1))
        cmd_model.print_log('UI core is instaed button event',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None) 
        with open(enumList.Other.MD_FILE,"r",encoding = "utf-8") as f:
            md_text = f.read()
            md_text = md_text.replace("{VERSION}",enumList.VERSION_INFO)
        cmd_model.print_log('UI core is read md file',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None) 
        self.ui.Md_Show.setText(md_text)
        cmd_model.print_log('UI core is set md text',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None) 
        self.ui.version.setText(enumList.VERSION_INFO)
        self.ui.ico.setPixmap(QPixmap(str(enumList.Other.APPICO)))
        self.ui.Main_instct_Button.clicked.connect(self.new_users)
        self.ui.Main_Lost_Password.clicked.connect(self.lost_password)
        cmd_model.print_log('UI core is set tab name',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        self.ui.tabWidget.setTabText(0, "启动")
        self.ui.tabWidget.setTabText(1, "游戏库")
        self.ui.tabWidget.setTabText(2, "下载与导入")
        self.ui.tabWidget.setTabText(3, "设置")
        self.ui.tabWidget.setTabText(4, "关于")
        cmd_model.print_log('UI core is set tab page',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None) 
        self.ui.tabWidget.setCurrentIndex(0)
        cmd_model.print_log('UI core is set style',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        self.ui.page.setStyleSheet(str(res_text.sk(enumList.theme.DARK)))
    def login(self):
        cmd_model.print_log('UI core login button is push',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        if not(self.ui.Main_ZhangHao_Input.text() == None or self.ui.Main_PassWord_Input.text() == None):
            ACC_W = self.ui.Main_ZhangHao_Input.text()
            PWD_W = hash(str(self.ui.Main_PassWord_Input.text()))
            cmd_model.print_log('UI core input box s make hash',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
            self.ui.Main_ZhangHao_Input.setText(" "*len(self.ui.Main_ZhangHao_Input.text()))
            self.ui.Main_PassWord_Input.setText(" "*len(self.ui.Main_PassWord_Input.text()))
            cmd_model.print_log('UI core PWD is make " "',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
    def exit(self):
        cmd_model.print_log('UI core exit by engine',enum_log.INFO,enum_model.ALL,'all',None)
        cmd_model.print_log(fileRW.RFTxtLine(self.uiui,0),enum_log.INFO,enum_model.ALL,'all',None)
        self.uiui.close()
        self.close()
    def setPage(self,valve,num):
        valve.setCurrentIndex(num)
        cmd_model.print_log(f"UI Core Set Page to {num+1} page",enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
    def lost_password(self):
        cmd_model.print_log(fileRW.RFTxtLine(self.uiui,1),enum_log.INFO,enum_model.ALL,'all',None)
    def new_users(self):
        cmd_model.print_log(fileRW.RFTxtLine(self.uiui,2),enum_log.INFO,enum_model.ALL,'all',None)