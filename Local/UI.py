import sys,os
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWebChannel import *
from PySide6.QtWebEngineCore import *
from PySide6.QtWebEngineWidgets import *
from ui_local_ui import Ui_MainWindow
import cmd_model
import enumList
import fileRW
import res_text
enum_log = enumList.enumList_log()
enum_model = enumList.enumList_model()
enum_child_model_UI = enumList.enumList_UI()
enum_child_model_core = enumList.enumList_Core()
class JsBridge_H(QObject):
    def __init__(self,owner):
        super().__init__()
        self.owner = owner
    @Slot()
    def H_onLaunchGame(self):
        self.owner.H_onLaunchGame()
    @Slot()
    def H_onCloseGame(self):
        self.owner.H_onCloseGame()
    @Slot()
    def H_onSelectVersion(self):
        self.owner.H_onSelectVersion()
    @Slot()
    def H_onOpenSetting(self):
        self.owner.H_onOpenSetting()
    @Slot()
    def H_onOfflineMode(self):
        self.owner.H_onOfflineMode()
    @Slot()
    def H_onLoginClick(self):
        self.owner.H_onLoginClick()
    @Slot()
    def H_onAvatarLeftClick(self):
        self.owner.H_onAvatarLeftClick()
    @Slot()
    def H_onAvatarRightClick(self):
        self.owner.H_onAvatarRightClick()
    @Slot(str)
    def H_onNicknameChanged(self,name:str):
        self.owner.H_onNicknameChanged(name)
class LuncherUI(QMainWindow):
    def __init__(self):
        super().__init__()
        #-------------------------init--------------------
        self.ui = Ui_MainWindow()
        cmd_model.print_log('UI core is init',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        self.ui.setupUi(self)
        cmd_model.print_log('UI core is setup',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        self.setWindowIcon(QIcon(enumList.Other.APPICO))
        self.setFixedSize(843, 636)
        cmd_model.print_log('UI core is set ico finish',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        self.setWindowTitle("Ne启动器")
        cmd_model.print_log('UI core is set window title',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        self.setPage(self.ui.stackedWidget,0)
        cmd_model.print_log('UI core load ui config',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None) 
        #----------------------------connect-----------------
        self.uiui = open(enumList.Other.UIUICFG,"r",encoding="utf-8")
        self.ui.Main_Login_Button.clicked.connect(self.login)
        self.ui.Main_Exit_Button.clicked.connect(self.exit)
        self.ui.Main_OffLine_Run.clicked.connect(lambda:self.setPage(self.ui.stackedWidget,1))
        self.ui.Main_instct_Button.clicked.connect(self.new_users)
        self.ui.Main_Lost_Password.clicked.connect(self.lost_password)
        cmd_model.print_log('UI core is instaed button event',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None) 
        #--------------------------set_md----------------------
        with open(enumList.Other.MD_FILE,"r",encoding = "utf-8") as f:
            md_text = f.read()
            md_text = md_text.replace("{VERSION}",enumList.VERSION_INFO)
        cmd_model.print_log('UI core is read md file',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None) 
        self.ui.Md_Show.setText(md_text)
        cmd_model.print_log('UI core is set md text',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None) 
        self.ui.version.setText(enumList.VERSION_INFO)
        self.ui.ico.setPixmap(QPixmap(str(enumList.Other.APPICO)))
        #--------------------set_tab_name---------------------
        cmd_model.print_log('UI core is set tab name',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        self.ui.tabWidget.setTabText(0, "启动")
        self.ui.tabWidget.setTabText(1, "游戏库")
        self.ui.tabWidget.setTabText(2, "下载与导入")
        self.ui.tabWidget.setTabText(3, "设置")
        self.ui.tabWidget.setTabText(4, "关于")
        cmd_model.print_log('UI core is set tab page',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None) 
        self.ui.tabWidget.setCurrentIndex(0)
        #-----------------------style---------------------------
        cmd_model.print_log('UI core is set style',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        self.ui.page.setStyleSheet(str(res_text.sk(enumList.theme.DARK)))
        #------------------------js-----------------------------
        cmd_model.print_log('Core is build js',enum_log.INFO,enum_model.CORE,enum_child_model_core.GAMEPMGR,None)
        self.js = JsBridge_H(self)
        #------------------------Home---------------------------
        cmd_model.print_log('UI core is HTML create js contenw JS id H_ ',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        self.chnnel_h = QWebChannel()
        self.chnnel_h.registerObject("bridge",self.js)
        self.ui.webEngineView.page().setWebChannel(self.chnnel_h)
        cmd_model.print_log('UI core is read run.html html',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        run_html = os.path.abspath("Local/run.html")
        self.ui.webEngineView.setUrl(QUrl.fromLocalFile(run_html))


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

    #-------------------------HOME-----------------------
    def H_onLaunchGame(self):
        cmd_model.print_log('Core is run game',enum_log.INFO,enum_model.CORE,enum_child_model_core.GAMEPMGR,None)
    def H_onCloseGame(self):
        cmd_model.print_log('Core is close game',enum_log.INFO,enum_model.CORE,enum_child_model_core.GAMEPMGR,None)
    def H_onSelectVersion(self):
        cmd_model.print_log('UI core is run change game',enum_log.INFO,enum_model.ALL,'all',None)
    def H_onOpenSetting(self):
        cmd_model.print_log('UI core is run game setting',enum_log.INFO,enum_model.ALL,'all',None)
    def H_onOfflineMode(self):
        cmd_model.print_log('Core is run off line',enum_log.INFO,enum_model.CORE,enum_child_model_core.GAMEPMGR,None)
    def H_onLoginClick(self):
        cmd_model.print_log('Core is run on line',enum_log.INFO,enum_model.CORE,enum_child_model_core.GAMEPMGR,None)
    def H_onAvatarLeftClick(self):
        cmd_model.print_log('UI core is run player setting',enum_log.INFO,enum_model.ALL,'all',None)
    def H_onAvatarRightClick(self):
        cmd_model.print_log('UI core is run users info',enum_log.INFO,enum_model.ALL,'all',None)
    def H_onNicknameChanged(self,name):
        cmd_model.print_log(f'UI core is run change name {name}',enum_log.INFO,enum_model.ALL,'all',None)