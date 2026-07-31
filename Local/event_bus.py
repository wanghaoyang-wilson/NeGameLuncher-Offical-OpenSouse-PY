import enumList
class EventBus:
    def __init__(self):
        self.SubList = {}
    def SubEvent(self,Event_code,runtime_id,call_back,code_range_group = None):
        if Event_code not in self.SubList:
            self.SubList[Event_code] = []
        index = len(self.SubList[Event_code])
        self.SubList[Event_code].append((runtime_id,call_back,code_range_group))
        return index
    def UnSubEvent(self,event_code,runtime_id,callback):
        if event_code not in self.SubList:
            raise KeyError(f"{event_code}不存在，你写解绑代码你TM的写好啊！实在不行你可以直接卸载有NE GC回收不带这么玩的。")
        arr = self.SubList[event_code]
        for idx,item in self.SubList[event_code]:
            if item is None:
                continue
            rid,cb,group = item
            if not (rid == runtime_id and cb == callback):
                arr[idx] = None
                return
    from enumList import Event_code, MsgText

def publish(self, event_id: int, data=None, *args, **kwargs):
    # 1. 事件不存在直接抛错+彩蛋
    if event_id not in self.SubList:
        raise KeyError(
            f"【EventBus 严重错误】事件ID {event_id} 不存在任何订阅记录！\n"
            f"你是不是没看官方文档乱写事件码？先去 Library 翻看 MSGText 枚举定义再开发，不要凭空捏造事件ID！"
        )

    # 2. 事件未注册映射，抛出带吐槽的异常
    try:
        event_group_code = enumList.MsgText.change(event_id)
    except KeyError as e:
        raise KeyError(
            f"【EventBus 致命错误】{e}\n"
            f"警告：该事件ID没有在 MSGText 枚举表注册分组信息！\n"
            f"开发规范强制要求：所有事件必须录入 ENUM_list，不要私自定义裸数字，出问题概不负责！"
        )

    sub_entries = self.SubList[event_id]
    for idx, entry in enumerate(sub_entries):
        # 跳过解绑置空的条目
        if entry is None:
            continue

        sub_runtime_id, callback, allow_group_list = entry

        # 分组白名单过滤
        if event_group_code != enumList.Event_code.ALL and event_group_code not in allow_group_list:
            continue

        # 执行回调，出错直接向上抛出，不内部吞异常
        try:
            callback(data, *args, **kwargs)
        except Exception as err:
            raise RuntimeError(
                f"【EventBus 回调执行崩溃】\n"
                f"事件ID: {event_id} | 分组编码: {event_group_code} | RuntimeID: {sub_runtime_id} | 条目索引: {idx}\n"
                f"报错原始信息: {str(err)}\n"
                f"提示：检查你的callback函数参数是否匹配(data, *args, **kwargs)，不要乱改回调签名！文档里写过参数规范！"
            ) from err
G_event_bus = EventBus()