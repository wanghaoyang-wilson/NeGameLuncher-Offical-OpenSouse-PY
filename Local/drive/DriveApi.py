# drive_plugin_api.py —— 官方 Drive API 示例驱动
# 演示：加载器(RunDriveCore)会把「注入上下文」绑定到每个驱动实例，
# 驱动通过 self.context / self.ctx 读取引擎注入的各种关键信息。
from typing import Any, Tuple, Optional, Dict, List
from pathlib import Path

import cmd_model
import enumList
from event_bus import G_event_bus
from jsonedit import ConfigManager

from drive_loding import RunDriveCore, DriveMetaData, DriveContext


class NeGameEngineDriveClass:
    REGISTER_NAME = "NL.Drive.DriveAPI"   # 修正拼写：原为 "NL.Deive.DriveAPI"
    def __init__(self):
        # 加载器会在加载后调用 bind_context(self, ctx) 注入上下文
        self.context: Optional[DriveContext] = None

    def bind_context(self, ctx: DriveContext):
        """加载器回调：接收注入的关键信息上下文。"""
        self.context = ctx

    def get_meta(self, key: str, default=None):
        """便捷读取注入信息。"""
        if self.context is not None:
            return self.context.get(key, default)
        return default

    def run(self, *argv):
        cmd_model.print_log(
            "驱动API已启动",
            enumList.enumList_log.INFO,
            Model=enumList.enumList_model.CORE,
            ChildModel=enumList.enumList_Core.GAMEPMGR,
            threadld=None,
        )
        # 读取注入信息（可能为空则显示默认）
        player = self.get_meta("player_name", "(未注入)")
        theme = self.get_meta("theme", "(未注入)")
        cmd_model.print_log(
            f"注入信息 player_name={player} theme={theme}",
            enumList.enumList_log.INFO,
        )
        cmd_model.print_log(f"arg:{argv}", enumList.enumList_log.INFO)
