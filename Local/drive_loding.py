# drive_loding.py
import os
import sys
import importlib
from typing import List, Optional, Dict, Callable, Any


class DriveMetaData:
    """驱动元数据，保存模块名、实例、是否启用、是否加载成功"""
    def __init__(self, module_name: str, instance: Any):
        self.module_name: str = module_name          # 驱动模块文件名(不带.py)
        self.instance: Any = instance                # NeGameEngineDriveClass实例
        self.enable: bool = True                     # 是否启用
        self.load_success: bool = True               # 是否加载成功


class RunDriveCore:
    def __init__(self):
        self.path_XiangDui = "/drive"
        self.path_JueDui = os.path.abspath(self.path_XiangDui)

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

    def _scan_and_load_all_drive(self):
        """扫描驱动目录，加载全部py驱动"""
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
                ins = drive_cls()
                meta = DriveMetaData(mod_name, ins)
                self._drive_meta_list.append(meta)
            except Exception as e:
                self._safe_error_callback(filename, e)
                meta = DriveMetaData(mod_name, None)
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
        【API】单独运行某个驱动
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

    def get_meta_by_modname(self, mod_name: str) -> Optional[DriveMetaData]:
        """【API】获取驱动元数据对象"""
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
        """【API】设置驱动启用/禁用，禁用后run_all不会执行它"""
        meta = self.get_meta_by_modname(mod_name)
        if meta is None:
            return False
        meta.enable = enable
        return True

    def hot_reload_drive(self, mod_name: str) -> bool:
        """
        【API】热重载单个驱动模块（修改py代码不用重启程序）
        注意：旧实例会丢弃，生成全新实例
        """
        try:
            # 1.获取旧模块
            old_mod = importlib.import_module(mod_name)
            new_mod = importlib.reload(old_mod)
            new_cls = getattr(new_mod, "NeGameEngineDriveClass")
            new_ins = new_cls()

            # 更新元数据
            meta = self.get_meta_by_modname(mod_name)
            if meta:
                meta.instance = new_ins
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
        【API】调用驱动实例任意方法
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

    def get_drive_count(self) -> Dict[str, int]:
        """【API】获取驱动统计信息 total/loaded/enabled"""
        total = len(self._drive_meta_list)
        loaded = sum(1 for m in self._drive_meta_list if m.load_success)
        enabled = sum(1 for m in self._drive_meta_list if m.load_success and m.enable)
        return {"total": total, "loaded": loaded, "enabled": enabled}

