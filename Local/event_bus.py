import enumList


class EventBus:
    """Ne Engine 事件总线：订阅/发布/解绑，带分组白名单过滤。"""

    def __init__(self):
        self.SubList = {}

    def SubEvent(self, Event_code, runtime_id, call_back, code_range_group=None):
        """
        订阅事件。
        :param code_range_group: 订阅者接受的分组白名单。
            传 enumList.Event_code.ALL(5) 或 None 表示接受所有分组；
            传单个分组编码(int) 或 分组编码列表/元组/集合(list/tuple/set) 时只接受指定分组。
        """
        if Event_code not in self.SubList:
            self.SubList[Event_code] = []
        index = len(self.SubList[Event_code])
        self.SubList[Event_code].append((runtime_id, call_back, code_range_group))
        return index

    def UnSubEvent(self, event_code, runtime_id, callback):
        """解绑事件：精确匹配 runtime_id + callback 后置空（不移除列表，保持索引稳定）。"""
        if event_code not in self.SubList:
            raise KeyError(
                f"{event_code}不存在，你写解绑代码你TM的写好啊！实在不行你可以直接卸载有NE GC回收不带这么玩的。"
            )
        arr = self.SubList[event_code]
        for idx, item in enumerate(arr):
            if item is None:
                continue
            rid, cb, group = item
            if rid == runtime_id and cb == callback:
                arr[idx] = None
                return True
        # 没找到目标订阅：容忍（幂等），并提示
        return False

    # ========== 分组白名单判定（统一入口） ==========
    @staticmethod
    def _accept_group(subscriber_groups, event_group_code) -> bool:
        """判断订阅者是否接收属于 event_group_code 的事件。"""
        # 订阅者未声明 或 声明 ALL -> 接受所有分组
        if subscriber_groups is None:
            return True
        if subscriber_groups == enumList.Event_code.ALL:
            return True
        # 单个分组编码
        if isinstance(subscriber_groups, int):
            return event_group_code == subscriber_groups
        # 可迭代集合（list/tuple/set...）
        if hasattr(subscriber_groups, "__iter__"):
            return event_group_code in subscriber_groups
        # 兜底：视为单个值比较
        return event_group_code == subscriber_groups

    def publish(self, event_id: int, data=None, *args, **kwargs):
        """发布事件：事件不存在时静默返回；分组白名单过滤后执行回调。"""
        if event_id not in self.SubList:
            return

        # ID <-> 名称翻译：映射缺失只告警，绝不把异常抛给引擎导致崩溃
        try:
            event_name = enumList.MsgText.change(event_id)
        except KeyError as e:
            event_name = None
            print(f"【EventBus 警告】事件ID {event_id} 未注册名称映射: {e}")

        # 分组归属：缺失只告警，不做致命拦截
        try:
            event_group_code = enumList.Code_Group[event_id]
        except KeyError:
            event_group_code = None
            print(f"【EventBus 警告】事件ID {event_id} 未在 Code_Group 配置分组")

        sub_entries = self.SubList[event_id]
        for idx, entry in enumerate(sub_entries):
            if entry is None:
                continue
            sub_runtime_id, callback, allow_group_list = entry

            # 分组白名单过滤：ALL/None 全部接收；否则按归属分组匹配
            if not self._accept_group(allow_group_list, event_group_code):
                continue

            try:
                callback(data, *args, **kwargs)
            except Exception as err:
                raise RuntimeError(
                    f"【EventBus 回调执行崩溃】\n"
                    f"事件ID: {event_id} | 事件名称:{event_name} | 分组编码: {event_group_code} | "
                    f"RuntimeID: {sub_runtime_id} | 条目索引: {idx}\n"
                    f"报错原始信息: {str(err)}\n"
                    f"提示：检查你的callback函数参数是否匹配(data, *args, **kwargs)，不要乱改回调签名！"
                ) from err


G_event_bus = EventBus()
