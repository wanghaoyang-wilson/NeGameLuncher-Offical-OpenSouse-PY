from pathlib import Path
import json

class ConfigManager:
    def __init__(self, config_file: Path):
        self.file_path: Path = config_file
        self.raw_data: dict = {}
        self._is_opened: bool = False

    # ========== 私有底层方法（外部禁止调用） ==========
    def _read_file(self, default_template: dict | None = None):
        """私有：底层读取磁盘文件"""
        if not self.file_path.exists():
            self.raw_data = default_template or {}
            self._write_file()
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.raw_data = json.load(f)
        except json.JSONDecodeError:
            self.raw_data = default_template or {}
            self._write_file()

    def _write_file(self):
        try:
            # 先把字典转成 JSON 字符串
            json_text = json.dumps(
                self.raw_data,
                indent=4,
                ensure_ascii=False,
                sort_keys=False
            )
            # 手动写入字符串，完全可控
            with open(self.file_path, "w", encoding="utf-8") as f:
                print(f"[写入中] {self.file_path} ...")
                f.write(json_text)
            print(f"[写入完成] {self.file_path}")
        except PermissionError:
            raise PermissionError(
                f"【写入权限错误】无法写入 {self.file_path}\n"
                f"不要放在系统保护目录运行！"
            )
        except Exception as e:
            raise OSError(f"【JSON写入异常】{e}")

    # ========== 唯一公开入口：open() 初始化加载 ==========
    def open(self, default_template: dict | None = None):
        """
        上层唯一文件加载入口
        :param default_template: 文件缺失/损坏时使用的默认配置
        :return: 自身实例，支持链式调用
        """
        self._read_file(default_template)
        self._is_opened = True
        return self

    # ========== 公开业务方法（必须先 open 才能用） ==========
    def _check_opened(self):
        """私有校验：必须先执行 open 才能读写"""
        if not self._is_opened:
            raise RuntimeError(
                "【配置未初始化错误】你还没有调用 .open() 加载配置文件！\n"
                "正确流程：cfg = ConfigManager(path).open()"
            )

    def get(self, path_str: str):
        """读取嵌套配置，例 get("A.B")"""
        self._check_opened()
        keys = path_str.split(".")
        current = self.raw_data
        for k in keys:
            if not isinstance(current, dict) or k not in current:
                raise KeyError(f"【路径缺失】{path_str} 解析失败，中断在 key: {k}")
            current = current[k]
        return current

    def edit(self, path_str: str, value, overwrite: bool = True):
        self._check_opened()
        if not isinstance(path_str, str):
            raise TypeError(f"路径参数必须是字符串，你传入了 {type(path_str)}")

        keys = path_str.split(".")
        current = self.raw_data
        target_key = keys[-1]

        # 逐层自动创建缺失字典
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]

        # 判断是否覆盖
        if overwrite or target_key not in current:
            current[target_key] = value
            
        self._write_file()