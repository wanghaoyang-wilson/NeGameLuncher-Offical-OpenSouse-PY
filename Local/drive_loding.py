# drive_loding.py
import os
import sys
import importlib
from PySide6.QtWidgets import QMessageBox
import ctypes
from typing import List, Optional, Dict, Callable, Any, Tuple
import cmd_model
import enumList

def pop_crash_dialog(title: str, msg: str):
    """弹出Windows错误弹窗，然后终止程序"""
    cmd_model.print_log(msg, enumList.enumList_log.FATAL, Model=enumList.enumList_model.CORE, ChildModel=enumList.enumList_Core.GAMEPMGR, threadld=None)
    sys.exit(1)


def _validate_register_name(reg_name: str) -> Tuple[bool, str]:
    """校验驱动注册名规则：至少2个.；不允许 \ / """
    if not isinstance(reg_name, str):
        return False, "注册名必须是字符串"
    if not reg_name.strip():
        return False, "注册名不能为空"
    if reg_name.count(".") < 2:
        return False, f"需要至少两个小数点'.'，当前仅有{reg_name.count('.')}个"
    for bad_char in ("\\", "/"):
        if bad_char in reg_name:
            return False, f"禁止包含非法字符：{bad_char}"
    return True, ""


class DriveMetaData:
    """驱动元数据，保存模块名、注册名、实例、是否启用、是否加载成功"""
    def __init__(self, module_name: str, register_name: str, instance: Any):
        self.module_name: str = module_name          # py模块文件名(不带.py)
        self.register_name: str = register_name      # 业务注册名，对外调用标识
        self.instance: Any = instance                # NeGameEngineDriveClass实例
        self.enable: bool = True                     # 是否启用
        self.load_success: bool = True               # 是否加载成功


class RunDriveCore:
    def __init__(self):
        self.path_XiangDui = "/drive"
        self.path_JueDui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drive")
        os.makedirs(self.path_JueDui, exist_ok=True)
        print(f"驱动目录绝对路径: {self.path_JueDui}")
        # 驱动元数据列表，替代单纯实例列表，存储更多信息
        self._drive_meta_list: List[DriveMetaData] = []
        # 错误回调，外部可以注册接收异常
        self.on_error: Optional[Callable[[str, Exception], None]] = None

    def init(self) -> None:
        """【核心入口API】初始化加载所有驱动，加载完成自动执行run()"""
        self._add_dir_to_syspath()
        self._scan_and_load_all_drive()
        self.run_all()

    def _add_dir_to_syspath(self):
        if self.path_JueDui not in sys.path:
            sys.path.append(self.path_JueDui)

    def _safe_error_callback(self, filename: str, err: Exception):
        """内部错误分发"""
        msg = f"驱动[{filename}]异常:{str(err)}"
        print(msg)
        if self.on_error is not None:
            try:
                self.on_error(filename, err)
            except:
                pass

    def _get_meta_by_regname(self, reg_name: str) -> Optional[DriveMetaData]:
        """内部：通过注册名获取元数据"""
        for m in self._drive_meta_list:
            if m.register_name == reg_name:
                return m
        return None

    def _scan_and_load_all_drive(self):
        """扫描驱动目录，加载全部py驱动，校验REGISTER_NAME，重复直接弹窗崩溃"""
        self._drive_meta_list.clear()
        if not os.path.exists(self.path_JueDui):
            print(f"警告：驱动目录不存在 {self.path_JueDui}")
            return
        for filename in os.listdir(self.path_JueDui):
            if not (filename.endswith(".py") and filename != "__init__.py"):
                continue
            mod_name = filename[:-3]
            try:
                drive_mod = importlib.import_module(mod_name)
                drive_cls = getattr(drive_mod, "NeGameEngineDriveClass")

                # 检查是否定义REGISTER_NAME
                if not hasattr(drive_cls, "REGISTER_NAME"):
                    pop_crash_dialog(
                        "驱动加载致命错误",
                        f"插件文件：{filename}\n"
                        "NeGameEngineDriveClass 缺少类属性 REGISTER_NAME\n"
                        "示例：REGISTER_NAME = \"app.module.sub\""
                    )
                reg_name = drive_cls.REGISTER_NAME

                # 格式校验
                valid, err_msg = _validate_register_name(reg_name)
                if not valid:
                    pop_crash_dialog(
                        "驱动注册名非法",
                        f"插件文件：{filename}\n注册名：{reg_name}\n错误：{err_msg}"
                    )

                # 查重：注册名全局唯一
                conflict_meta = self._get_meta_by_regname(reg_name)
                if conflict_meta is not None:
                    pop_crash_dialog(
                        "驱动注册名冲突【致命】",
                        f"注册名 [{reg_name}] 重复！\n"
                        f"已占用模块：{conflict_meta.module_name}.py\n"
                        f"冲突模块：{filename}"
                    )

                ins = drive_cls()
                meta = DriveMetaData(mod_name, reg_name, ins)
                self._drive_meta_list.append(meta)

            except Exception as e:
                self._safe_error_callback(filename, e)
                meta = DriveMetaData(mod_name, "", None)
                meta.load_success = False
                self._drive_meta_list.append(meta)

    def run_all(self) -> None:
        """【API】运行所有【启用状态】驱动的run()方法"""
        for meta in self._drive_meta_list:
            if not meta.load_success or not meta.enable:
                continue
            ins = meta.instance
            if hasattr(ins, "run") and callable(ins.run):
                try:
                    ins.run()
                except Exception as e:
                    self._safe_error_callback(meta.module_name, e)

    def run_single(self, module_name: str) -> bool:
        """
        【API】单独运行某个驱动（按模块名）
        :param module_name: 驱动模块名(不带.py)
        :return: True成功 False失败
        """
        meta = self.get_meta_by_modname(module_name)
        if meta is None or not meta.load_success or not meta.enable:
            return False
        ins = meta.instance
        if hasattr(ins, "run") and callable(ins.run):
            try:
                ins.run()
                return True
            except Exception as e:
                self._safe_error_callback(module_name, e)
        return False

    # ========== 原有：按模块名查找（全部保留） ==========
    def get_meta_by_modname(self, mod_name: str) -> Optional[DriveMetaData]:
        """【API】获取驱动元数据对象（按模块名）"""
        for m in self._drive_meta_list:
            if m.module_name == mod_name:
                return m
        return None

    def get_drive_instance(self, mod_name: str) -> Optional[Any]:
        """【API】按模块名获取驱动实例 NeGameEngineDriveClass"""
        meta = self.get_meta_by_modname(mod_name)
        if meta and meta.load_success:
            return meta.instance
        return None

    def get_all_instances(self) -> List[Any]:
        """【API】获取全部加载成功的驱动实例列表（原始实例）"""
        return [meta.instance for meta in self._drive_meta_list if meta.load_success]

    def get_all_mod_names(self) -> List[str]:
        """【API】获取所有驱动模块名称列表"""
        return [meta.module_name for meta in self._drive_meta_list]

    def set_drive_enable(self, mod_name: str, enable: bool) -> bool:
        """【API】设置驱动启用/禁用，禁用后run_all不会执行它（按模块名）"""
        meta = self.get_meta_by_modname(mod_name)
        if meta is None:
            return False
        meta.enable = enable
        return True

    def hot_reload_drive(self, mod_name: str) -> bool:
        """
        【API】热重载单个驱动模块（修改py代码不用重启程序）
        注意：旧实例会丢弃，生成全新实例；热重载同样校验REGISTER_NAME
        """
        try:
            old_mod = importlib.import_module(mod_name)
            new_mod = importlib.reload(old_mod)
            new_cls = getattr(new_mod, "NeGameEngineDriveClass")

            # 热重载也要校验注册名
            if not hasattr(new_cls, "REGISTER_NAME"):
                self._safe_error_callback(mod_name, Exception("热重载：缺少REGISTER_NAME"))
                return False
            new_reg = new_cls.REGISTER_NAME
            valid, err = _validate_register_name(new_reg)
            if not valid:
                self._safe_error_callback(mod_name, Exception(f"热重载注册名非法:{err}"))
                return False

            meta = self.get_meta_by_modname(mod_name)
            if meta is None:
                return False

            # 如果注册名发生变化，检查是否和其他驱动冲突
            if meta.register_name != new_reg:
                conflict = self._get_meta_by_regname(new_reg)
                if conflict is not None and conflict.module_name != mod_name:
                    self._safe_error_callback(mod_name, Exception(f"热重载注册名冲突:{new_reg}"))
                    return False
            new_ins = new_cls()
            meta.instance = new_ins
            meta.register_name = new_reg
            meta.load_success = True
            return True
        except Exception as e:
            self._safe_error_callback(mod_name, e)
            return False

    def reload_all(self):
        """【API】全部驱动重新扫描+热重载，会清空旧实例"""
        self._scan_and_load_all_drive()
        self.run_all()

    def call_drive_method(self, mod_name: str, method_name: str, *args, **kwargs) -> Optional[Any]:
        """
        【API】调用驱动实例任意方法（按模块名）
        example: core.call_drive_method("test_drive", "some_func", 123, name="abc")
        """
        ins = self.get_drive_instance(mod_name)
        if ins is None:
            return None
        if not hasattr(ins, method_name):
            return None
        func = getattr(ins, method_name)
        if callable(func):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self._safe_error_callback(mod_name, e)
        return None

    def call_drive_method_safe(self, mod_name: str, method_name: str, *args, **kwargs) -> Tuple[bool, Any, Optional[Exception]]:
        """
        【新增API】安全调用驱动方法（按模块名），返回完整调用状态，区分返回None和调用失败
        """
        ins = self.get_drive_instance(mod_name)
        if ins is None:
            return False, None, None
        if not hasattr(ins, method_name):
            return False, None, None
        func = getattr(ins, method_name)
        if not callable(func):
            return False, None, None
        try:
            result = func(*args, **kwargs)
            return True, result, None
        except Exception as e:
            self._safe_error_callback(mod_name, e)
            return False, None, e

    def call_all_drives_method(self, method_name: str, *args, **kwargs) -> Dict[str, Tuple[bool, Any, Optional[Exception]]]:
        """
        【新增API】批量调用所有已加载、已启用驱动的同一个方法
        返回dict key=模块名 value=(成功标记,返回值,异常)
        """
        output: Dict[str, Tuple[bool, Any, Optional[Exception]]] = {}
        for meta in self._drive_meta_list:
            if not meta.load_success or not meta.enable:
                continue
            mod = meta.module_name
            ok, val, exc = self.call_drive_method_safe(mod, method_name, *args, **kwargs)
            output[mod] = (ok, val, exc)
        return output

    def get_drive_count(self) -> Dict[str, int]:
        """【API】获取驱动统计信息 total/loaded/enabled"""
        total = len(self._drive_meta_list)
        loaded = sum(1 for m in self._drive_meta_list if m.load_success)
        enabled = sum(1 for m in self._drive_meta_list if m.load_success and m.enable)
        return {"total": total, "loaded": loaded, "enabled": enabled}

    # ===================== 新增：【按注册名】对外API（推荐业务优先使用这套） =====================
    def get_meta_by_regname(self, reg_name: str) -> Optional[DriveMetaData]:
        """【API】通过注册名获取元数据"""
        return self._get_meta_by_regname(reg_name)

    def get_drive_instance_by_regname(self, reg_name: str) -> Optional[Any]:
        """【API】通过注册名获取驱动实例"""
        meta = self._get_meta_by_regname(reg_name)
        if meta and meta.load_success:
            return meta.instance
        return None

    def call_drive_method_by_reg(self, reg_name: str, method_name: str, *args, **kwargs) -> Optional[Any]:
        """【API】通过注册名调用驱动方法，出错返回None"""
        ins = self.get_drive_instance_by_regname(reg_name)
        if ins is None:
            return None
        if not hasattr(ins, method_name):
            return None
        func = getattr(ins, method_name)
        if callable(func):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self._safe_error_callback(reg_name, e)
        return None

    def call_drive_method_safe_by_reg(self, reg_name: str, method_name: str, *args, **kwargs) -> Tuple[bool, Any, Optional[Exception]]:
        """【API】安全调用，通过注册名；返回 (ok,result,exception)"""
        ins = self.get_drive_instance_by_regname(reg_name)
        if ins is None:
            return False, None, None
        if not hasattr(ins, method_name):
            return False, None, None
        func = getattr(ins, method_name)
        if not callable(func):
            return False, None, None
        try:
            res = func(*args, **kwargs)
            return True, res, None
        except Exception as e:
            self._safe_error_callback(reg_name, e)
            return False, None, e

    def set_drive_enable_by_reg(self, reg_name: str, enable: bool) -> bool:
        """【API】按注册名启用/禁用驱动"""
        meta = self._get_meta_by_regname(reg_name)
        if meta is None:
            return False
        meta.enable = enable
        return True