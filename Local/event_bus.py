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
    def publish(self,event_code,*args,**kwargs):
        if event_code not in self.SubList:
            return
        arr = self.SubList[event_code]
        for item in arr:
            if item is None:
                continue
            rid,callback,code_range_group = item
            run = False
            if code_range_group is None:
                run = True
            else:
                min_c,max_c = code_range_group
                if min_c <= event_code <= max_c:
                    run = True
            if not run:
                continue
            try:
                callback(*args,**kwargs)
            except Exception as e:
                print(e)
G_event_bus = EventBus()