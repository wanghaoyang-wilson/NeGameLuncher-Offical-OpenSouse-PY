import sys,os,json
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWebChannel import *
from PySide6.QtWebEngineCore import *
from PySide6.QtWebEngineWidgets import *
from ui_local_ui import Ui_MainWindow
from event_bus import G_event_bus
import cmd_model
import enumList
import fileRW
import res_text
import event_core
import drive_mgr
os.environ["QT_API"] = "pyside6"
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "PySide6/plugins"
code = enumList.MsgCode()
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
class RepoQJSObject(QObject):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner

    @Slot()
    def RunGame(self):
        self.owner.H_onLaunchGame()
    @Slot()
    def ChangeGame(self):
        self.owner.H_onSelectVersion()


class PyNotifyBridge(QObject):
    """
    Python -> JS 反向推送桥：
    注册到 QWebChannel 后，JS 侧订阅 pySignal 信号即可接收 Python 主动推送的事件。
    用法：self.py_bridge.emit_py("playerNameChanged", "NeHyird")
    JS 侧：channel.objects.pyBridge.pySignal.connect((topic, payload)=>{...})
    """
    pySignal = Signal(str, str)

    def emit_py(self, topic: str, payload: str = ""):
        """从 Python 主动向 JS 推送事件（payload 建议传 JSON 字符串）。"""
        self.pySignal.emit(topic, payload)
EMPTY_PLACEHOLDER_UID = "placeholder_empty_warehouse"

class WarehouseListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data_list = []
        self._placeholder_item = {
            "uid": EMPTY_PLACEHOLDER_UID,
            "icon_key": "",
            "name": "仓库暂无物品",
            "version": "",
            "count": 0,
            "is_placeholder": True
        }

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            if len(self._data_list) == 0:
                return 1
            return len(self._data_list)
        return 0

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if len(self._data_list) == 0:
            row_data = self._placeholder_item
        else:
            row_data = self._data_list[index.row()]

        if role == Qt.DisplayRole:
            return row_data["name"]
        if role == Qt.UserRole:
            return row_data
        return None

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.NoItemFlags
        # 无数据 = 占位行，禁止选中
        if len(self._data_list) == 0:
            return Qt.NoItemFlags
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def add_item(self, icon_key: str, name: str, version: str, uid: str, count: int = 1):
        item = {
            "uid": uid,
            "icon_key": icon_key,
            "name": name,
            "version": version,
            "count": count,
            "is_placeholder": False
        }
        self.beginInsertRows(QModelIndex(), len(self._data_list), len(self._data_list))
        self._data_list.append(item)
        self.endInsertRows()

    def clear_all(self):
        self.beginResetModel()
        self._data_list.clear()
        self.endResetModel()

    def set_item_count(self, target_uid: str, new_count: int):
        for idx, item in enumerate(self._data_list):
            if item["uid"] == target_uid:
                item["count"] = new_count
                self.dataChanged.emit(self.index(idx, 0), self.index(idx, 0))
                break


class WarehouseManager:
    def __init__(self, list_view: QListView):
        self._view: QListView = list_view
        self._model = WarehouseListModel()
        self._view.setModel(self._model)
        self._view.clicked.connect(self._on_item_click)

        # 强制外部注册点击回调，未注册调用会抛出异常
        self._click_callback = None

    def set_click_callback(self, callback):
        """
        注册点击回调
        回调签名: func(index: int) -> None
        """
        self._click_callback = callback

    def _on_item_click(self, index: QModelIndex):
        if not self._click_callback:
            raise RuntimeError("必须调用 set_click_callback 注册点击回调函数！")
        row_idx = index.row()
        self._click_callback(row_idx)

    def add_item(self, icon_key: str, name: str, version: str, uid: str, count: int = 1):
        self._model.add_item(icon_key, name, version, uid, count)

    def clear(self):
        self._model.clear_all()

    # 内置JSON解析工具
    @staticmethod
    def parse_json(raw_str: str):
        try:
            return json.loads(raw_str)
        except Exception as e:
            return {}

    def set_list(self, json_obj: dict):
        """
        接收字典 {"1": {...}, "2": {...}} 格式
        自动清空原有列表，批量载入物品
        允许 icon_key 为空字符串
        """
        self.clear()
        # 按键从小到大排序载入
        sorted_keys = sorted(json_obj.keys(), key=lambda k: int(k))
        for key in sorted_keys:
            data = json_obj[key]
            icon = data.get("icon_key", "")
            name = data.get("name", "")
            ver = data.get("version", "")
            uid = data.get("uid", "")
            cnt = data.get("count", 1)
            self.add_item(icon, name, ver, uid, cnt)

class LuncherUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # Python->JS 通道状态（提前初始化，供 apply_theme 等调用 _call_js 使用）
        self._js_ready = False
        self._js_pending = []
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
        # 主题应用到全局（QApplication），而不是只套单个 page，保证深/浅色铺满整个窗口
        self._current_theme = enumList.theme.DARK
        self.apply_theme(self._current_theme)
        #------------------------js-----------------------------
        cmd_model.print_log('Core is build js',enum_log.INFO,enum_model.CORE,enum_child_model_core.GAMEPMGR,None)
        self.js = JsBridge_H(self)
        #------------------------Home---------------------------
        cmd_model.print_log('UI core is HTML create js contenw JS id H_ ',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        self.chnnel_h = QWebChannel()
        self.chnnel_h.registerObject("bridge",self.js)
        # 注册 Python->JS 反向推送桥
        self.py_bridge = PyNotifyBridge(self)
        self.chnnel_h.registerObject("pyBridge", self.py_bridge)
        self.ui.webEngineView.page().setWebChannel(self.chnnel_h)
        # Python->JS 直接调用：等页面加载完成后再调用（避免 setPlayerName is not defined）
        self._js_initial_name = event_core.event_core.Home_Player_Name_get()
        cmd_model.print_log('UI core is read run.html html',enum_log.INFO,enum_model.UI,enum_child_model_UI.UI,None)
        run_html = os.path.abspath("Local/run.html")
        self.ui.webEngineView.setUrl(QUrl.fromLocalFile(run_html))
        self.ui.webEngineView.page().loadFinished.connect(self._on_page_loaded)
        #-------------------------repo------------------------
        self.WarehouseListModel = WarehouseListModel()
        self.WarehouseManager = WarehouseManager(self.ui.listView)
        self.WarehouseManager.set_click_callback(self.repo_return_index)
        G_event_bus.SubEvent(code.EVENT_GAME_CHANGE,0,self.test,enumList.Event_code.UI)

    # ===================== Python -> JS 双向桥 =====================
    def _call_js(self, func_name: str, *args):
        """
        安全调用页面里的 JS 函数：参数用 JSON 序列化（避免引号/命名冲突），
        页面未加载完成时先排队，loadFinished 后统一执行。
        """
        args_json = ", ".join(json.dumps(a, ensure_ascii=False) for a in args)
        script = f"{func_name}({args_json});"
        page = self.ui.webEngineView.page()
        if self._js_ready:
            try:
                page.runJavaScript(script)
            except Exception as e:
                cmd_model.print_log(f"Python->JS 调用 {func_name} 异常:{e}", enum_log.ERROR)
        else:
            self._js_pending.append(script)

    def push_to_js(self, topic: str, payload=""):
        """Python 主动向 JS 推送事件（走 QWebChannel 信号，双向通信的 Python->JS 通道）。"""
        self.py_bridge.emit_py(topic, payload)

    def _on_page_loaded(self, ok: bool):
        """页面加载完成后：刷新状态并补发排队的 JS 调用。"""
        self._js_ready = True
        # 初始状态同步
        self._call_js("setPlayerName", self._js_initial_name)
        self._call_js("applyTheme", self._current_theme)
        # 补发排队调用
        for script in self._js_pending:
            self.ui.webEngineView.page().runJavaScript(script)
        self._js_pending.clear()
        cmd_model.print_log(f"页面加载完成 ok={ok}，Python->JS 通道就绪", enum_log.INFO)

    # ===================== 主题 =====================
    def apply_theme(self, theme):
        """应用主题到全局：QSS 全局生效 + 通知 HTML 同步切换。"""
        self._current_theme = theme
        qss = res_text.read_qss(theme)
        QApplication.instance().setStyleSheet(qss)
        # 通知前端切换配色
        try:
            self._call_js("applyTheme", theme)
        except Exception as e:
            cmd_model.print_log(f"推送主题到 HTML 异常:{e}", enum_log.INFO)
        cmd_model.print_log(f"主题已应用到全局: {theme}", enum_log.INFO)

    def switch_theme(self, theme):
        """对外切换主题入口。"""
        self.apply_theme(theme)

    def set_player_name_ui(self, name: str):
        """Python 主动更新前端玩家名（改名字后调用）。"""
        self._call_js("setPlayerName", name)

    def test(self):
        print("aaa")
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
        log = "\r".join(cmd_model.print_list)
        fileRW.write_file(f"{enumList.LOGDIRROOT}/log.txt", log)
        self.uiui.close()
        self.close()
    def closeEvent(self, event):
        self.exit()
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
        G_event_bus.publish(code.EVENT_GAME_START)
    def H_onCloseGame(self):
        cmd_model.print_log('Core is close game',enum_log.INFO,enum_model.CORE,enum_child_model_core.GAMEPMGR,None)
        G_event_bus.publish(code.EVENT_GAME_STOP)
    def H_onSelectVersion(self):
        cmd_model.print_log('UI core is run change game',enum_log.INFO,enum_model.ALL,'all',None)
        G_event_bus.publish(code.EVENT_GAME_CHANGE)
    def H_onOpenSetting(self):
        cmd_model.print_log('UI core is run game setting',enum_log.INFO,enum_model.ALL,'all',None)
        G_event_bus.publish(code.EVENT_GAME_SETTING)
    def H_onOfflineMode(self):
        cmd_model.print_log('Core is run off line',enum_log.INFO,enum_model.CORE,enum_child_model_core.GAMEPMGR,None)
        G_event_bus.publish(code.EVENT_PLAYER_RUN_OFFLINE)
    def H_onLoginClick(self):
        cmd_model.print_log('Core is run on line',enum_log.INFO,enum_model.CORE,enum_child_model_core.GAMEPMGR,None)
    def H_onAvatarLeftClick(self):
        cmd_model.print_log('UI core is run player setting',enum_log.INFO,enum_model.ALL,'all',None)
        G_event_bus.publish(code.EVENT_PLAYER_SETTING)
    def H_onAvatarRightClick(self):
        cmd_model.print_log('UI core is run users info',enum_log.INFO,enum_model.ALL,'all',None)
        G_event_bus.publish(code.EVENT_PLAYER_INFO)
    def H_onNicknameChanged(self,name):
        cmd_model.print_log(f'UI core is run change name {name}',enum_log.INFO,enum_model.ALL,'all',None)
        G_event_bus.publish(code.EVENT_PLAYER_CHANGE_NAME,name)
 
    #----------------------------repo-----------------------
    def repo_return_index(self,index):
        print(index)
