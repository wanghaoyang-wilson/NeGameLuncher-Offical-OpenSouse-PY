"""
系统与运行环境信息采集模块
模块名称: system_env_collector
用途: 采集跨平台硬件信息、Python环境、pip依赖、当前进程状态
支持两种工作模式：get模式(返回字典，可序列化为JSON) / print模式(控制台直接打印)
支持模块单独开关采集项、全局超时控制；预留多语言翻译接口，默认中文语言包

【返回JSON顶层字段说明】
{
  "os": {},                # 操作系统信息
  "python": {},            # Python解释器、pip版本、已安装包列表
  "cpu": {},               # CPU型号、核心数、频率、CPU使用率
  "memory": {},            # 系统内存总量/可用/已用，单位GB
  "disks": [{}, ...],      # 磁盘分区数组，每个元素为单个分区信息
  "gpus": [{}, ...],       # 显卡数组，多显卡会返回多条
  "process": {}            # 当前Python进程自身运行状态（PID、内存、线程等）
}

【各子字段详情】
1. os 操作系统
{
  "system": str,          # Windows / Linux / Darwin(macOS)
  "release": str,         # 系统版本号
  "version": str,         # 系统详细版本
  "machine": str,         # 硬件架构 x86_64 / AMD64 / arm64
  "arch": str,            # 位宽 32bit / 64bit
  "node": str             # 主机名
}

2. python Python环境信息
{
  "version": str,                     # Python完整版本字符串
  "version_info": {"major","minor","micro","releaselevel"}, # 版本分段数字
  "executable": str,                  # python解释器完整路径
  "prefix": str,                      # 环境根目录（虚拟环境识别）
  "sys_path": list[str],              # Python模块搜索路径列表
  "pip_version": str,                 # pip版本字符串
  "installed_packages": [{"name":"","version":""}, ...] # 当前环境全部pip包
}

3. cpu CPU信息
{
  "brand": str,                     # CPU完整型号（需要py-cpuinfo）
  "physical_cores": int | None,     # 物理核心数
  "logical_cores": int | None,      # 逻辑线程数
  "cpu_freq_current": float | None, # 当前频率 MHz
  "cpu_freq_max": float | None,     # 最大睿频 MHz
  "cpu_usage_total": float          # 整机CPU占用百分比
}

4. memory 内存信息
{
  "total_bytes": int,
  "total_gb": float,
  "available_bytes": int,
  "available_gb": float,
  "used_bytes": int,
  "used_gb": float,
  "percent_used": float
}

5. disks 磁盘数组（每个分区）
{
  "device": str,
  "mountpoint": str,
  "fstype": str,
  "total_gb": float,
  "used_gb": float,
  "free_gb": float,
  "percent_used": float,
  "warning": str | None  # 权限不足时存在此字段
}

6. gpus 显卡数组
{
  "name": str,
  "driver_version": str,
  "vram_gb": float | None,
  "note": str | None     # 缺少依赖/读取失败时出现
}

7. process 当前进程信息
{
  "pid": int,
  "create_time": float,    # 进程启动时间戳
  "rss_mb": float,         # 物理内存占用 MB
  "vms_mb": float,         # 虚拟内存占用 MB
  "cpu_percent": float,    # 本进程CPU占用
  "thread_count": int      # 进程内线程数量
}

【函数入参说明】
def get_system_and_env_info(
    mode: str = "get",               # 工作模式："get" 返回字典；"print" 直接控制台输出
    enable_os: bool = True,
    enable_python: bool = True,
    enable_cpu: bool = True,
    enable_memory: bool = True,
    enable_disks: bool = True,
    enable_gpus: bool = True,
    enable_process: bool = True,
    python_fetch_pip_packages: bool = True,
    timeout: float = 5.0,            # 全局超时，单位秒，超时则跳过当前采集模块
    language: str = "zh-CN"          # 语言包标识，预留接口：zh-CN / en-US，默认中文
) -> Dict[str, Any] | None:
    - mode="get"：返回采集结果字典，可直接json序列化
    - mode="print"：控制台打印信息，函数返回None
    - timeout：全局超时，任一模块采集超过该时间直接跳过，防止卡死
    - language：语言标识，预留多语言翻译接口，用于print模式展示文本翻译

【语言包预留说明】
内置翻译字典 `LANG_PACKS`，key为内部字段名，value为对应语言显示文本
新增语言只需要在LANG_PACKS内增加一组key-value，无需改动采集逻辑
示例：
LANG_PACKS["zh-CN"]["gpu_name"] = "显卡型号"
LANG_PACKS["en-US"]["gpu_name"] = "GPU Name"

【依赖说明】
pip install psutil py-cpuinfo wmi
> wmi：仅Windows平台读取显卡所需；Linux/macOS无需安装wmi
> py-cpuinfo：读取CPU型号，不安装则cpu.brand字段提示缺少依赖

【重要警告】
1. python_fetch_pip_packages=True 会调用子进程执行pip list，有短暂阻塞！
   ❌ 禁止放在渲染主循环、像素for循环内
   ✅ 仅程序启动时、崩溃日志导出时调用一次
2. 采集整机CPU占用有0.1s采样等待时间，同样不要高频调用
3. 返回值是原生Python字典，直接使用 json.dumps() 转为JSON字符串
4. timeout超时是模块级保护，每个采集模块单独计时，超时直接跳过该模块，不中断整体采集
"""
import platform
import sys
import json
import subprocess
import os
import psutil
import signal
from typing import Dict, Any, Optional


# ===================== 语言包【预留接口，后续扩展】 =====================
LANG_PACKS = {
    "zh-CN": {
        "title_os": "操作系统信息",
        "title_python": "Python运行环境",
        "title_cpu": "CPU信息",
        "title_memory": "内存信息",
        "title_disks": "磁盘分区",
        "title_gpus": "显卡列表",
        "title_process": "当前进程信息",
        "system": "系统名称",
        "release": "系统发行版本",
        "version": "系统详细版本",
        "machine": "硬件架构",
        "arch": "系统位宽",
        "node": "主机名",
        "python_version": "Python版本",
        "executable": "解释器路径",
        "pip_version": "Pip版本",
        "installed_packages": "已安装依赖包",
        "brand": "CPU型号",
        "physical_cores": "物理核心",
        "logical_cores": "逻辑线程",
        "cpu_freq_current": "当前频率(MHz)",
        "cpu_freq_max": "最大睿频(MHz)",
        "cpu_usage_total": "整机CPU占用(%)",
        "total_gb": "总容量(GB)",
        "available_gb": "可用内存(GB)",
        "used_gb": "已使用(GB)",
        "percent_used": "使用率(%)",
        "mountpoint": "挂载点",
        "fstype": "文件系统",
        "gpu_name": "显卡型号",
        "driver_version": "驱动版本",
        "vram_gb": "显存(GB)",
        "pid": "进程PID",
        "rss_mb": "物理内存占用(MB)",
        "vms_mb": "虚拟内存占用(MB)",
        "process_cpu_percent": "进程CPU占用(%)",
        "thread_count": "线程数量",
        "timeout_skip": "【超时】模块采集超时，已跳过",
        "error_skip": "【错误】采集失败",
    },
    "en-US": {
        "title_os": "OS Information",
        "title_python": "Python Environment",
        "title_cpu": "CPU Information",
        "title_memory": "Memory Information",
        "title_disks": "Disk Partitions",
        "title_gpus": "GPU List",
        "title_process": "Current Process Info",
        "system": "System",
        "release": "Release",
        "version": "Version",
        "machine": "Architecture",
        "arch": "Bit Arch",
        "node": "Hostname",
        "python_version": "Python Version",
        "executable": "Python Executable",
        "pip_version": "Pip Version",
        "installed_packages": "Installed Packages",
        "brand": "CPU Brand",
        "physical_cores": "Physical Cores",
        "logical_cores": "Logical Threads",
        "cpu_freq_current": "Current Freq(MHz)",
        "cpu_freq_max": "Max Freq(MHz)",
        "cpu_usage_total": "Total CPU Usage(%)",
        "total_gb": "Total(GB)",
        "available_gb": "Available(GB)",
        "used_gb": "Used(GB)",
        "percent_used": "Usage(%)",
        "mountpoint": "Mount Point",
        "fstype": "File System",
        "gpu_name": "GPU Name",
        "driver_version": "Driver Version",
        "vram_gb": "VRAM(GB)",
        "pid": "Process PID",
        "rss_mb": "RSS Memory(MB)",
        "vms_mb": "VMS Memory(MB)",
        "process_cpu_percent": "Process CPU Usage(%)",
        "thread_count": "Thread Count",
        "timeout_skip": "[Timeout] Module skipped",
        "error_skip": "[Error] Collect failed",
    }
}


class ModuleTimeout(Exception):
    """自定义模块采集超时异常"""
    pass


def timeout_handler(signum, frame):
    raise ModuleTimeout()


def get_system_and_env_info(
    mode: str = "get",
    enable_os: bool = True,
    enable_python: bool = True,
    enable_cpu: bool = True,
    enable_memory: bool = True,
    enable_disks: bool = True,
    enable_gpus: bool = True,
    enable_process: bool = True,
    python_fetch_pip_packages: bool = True,
    timeout: float = 5.0,
    language: str = "zh-CN"
) -> Optional[Dict[str, Any]]:
    """
    获取跨平台系统硬件信息 + Python运行环境 + pip依赖
    :param mode: 运行模式，可选 "get" | "print"
    :param enable_os: 是否采集操作系统信息
    :param enable_python: 是否采集Python环境基础信息
    :param enable_cpu: 是否采集CPU信息
    :param enable_memory: 是否采集内存信息
    :param enable_disks: 是否采集磁盘分区信息
    :param enable_gpus: 是否采集显卡信息
    :param enable_process: 是否采集当前进程运行状态
    :param python_fetch_pip_packages: 是否额外调用pip list读取全部已安装包（耗时）
    :param timeout: 全局超时时间（秒），单个模块超过该时间直接跳过
    :param language: 语言包标识 zh-CN / en-US
    :return: mode="get" 返回字典；mode="print" 返回None，直接打印控制台
    """
    # 语言包兜底，不存在的语言自动切中文
    lang = LANG_PACKS.get(language, LANG_PACKS["zh-CN"])
    result: Dict[str, Any] = {}

    # Windows不支持signal SIGALRM，超时仅在Linux/macOS生效；Windows靠try-except做软超时
    use_signal_timeout = platform.system() != "Windows"

    def run_with_timeout(collect_func):
        try:
            if use_signal_timeout:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(timeout))
            data = collect_func()
            if use_signal_timeout:
                signal.alarm(0)
            return data
        except ModuleTimeout:
            return {"__skip": True, "msg": lang["timeout_skip"]}
        except Exception:
            return {"__skip": True, "msg": lang["error_skip"]}

    # ========== 1. OS系统信息 ==========
    if enable_os:
        def collect_os():
            return {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "arch": platform.architecture()[0],
                "node": platform.node(),
            }
        os_data = run_with_timeout(collect_os)
        if not os_data.get("__skip"):
            result["os"] = os_data
        else:
            result["os"] = os_data

    # ========== 2. Python环境信息 ==========
    if enable_python:
        def collect_python():
            py_info = {
                "version": sys.version,
                "version_info": {
                    "major": sys.version_info.major,
                    "minor": sys.version_info.minor,
                    "micro": sys.version_info.micro,
                    "releaselevel": sys.version_info.releaselevel,
                },
                "executable": sys.executable,
                "prefix": sys.prefix,
                "sys_path": sys.path,
            }
            # 获取pip版本
            try:
                pip_ver = subprocess.check_output([sys.executable, "-m", "pip", "--version"],
                                                  text=True, stderr=subprocess.STDOUT).strip()
            except Exception as e:
                pip_ver = f"无法获取: {str(e)}"
            py_info["pip_version"] = pip_ver

            if python_fetch_pip_packages:
                try:
                    pip_list_raw = subprocess.check_output([sys.executable, "-m", "pip", "list", "--format=json"],
                                                            text=True, stderr=subprocess.STDOUT)
                    pip_packages = json.loads(pip_list_raw)
                except Exception as e:
                    pip_packages = [{"error": f"获取包列表失败: {str(e)}"}]
                py_info["installed_packages"] = pip_packages
            return py_info
        py_data = run_with_timeout(collect_python)
        if not py_data.get("__skip"):
            result["python"] = py_data
        else:
            result["python"] = py_data

    # ========== 3. CPU信息 ==========
    if enable_cpu:
        def collect_cpu():
            cpu_info = {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "cpu_freq_current": psutil.cpu_freq().current if psutil.cpu_freq() else None,
                "cpu_freq_max": psutil.cpu_freq().max if psutil.cpu_freq() else None,
                "cpu_usage_total": psutil.cpu_percent(interval=0.1),
            }
            try:
                import cpuinfo
                cinfo = cpuinfo.get_cpu_info()
                cpu_info["brand"] = cinfo.get("brand_raw", "unknown")
            except ImportError:
                cpu_info["brand"] = "需要安装 py-cpuinfo 才能读取CPU型号"
            return cpu_info
        cpu_data = run_with_timeout(collect_cpu)
        if not cpu_data.get("__skip"):
            result["cpu"] = cpu_data
        else:
            result["cpu"] = cpu_data

    # ========== 4. 内存信息 ==========
    if enable_memory:
        def collect_memory():
            mem = psutil.virtual_memory()
            return {
                "total_bytes": mem.total,
                "total_gb": round(mem.total / (1024 ** 3), 2),
                "available_bytes": mem.available,
                "available_gb": round(mem.available / (1024 ** 3), 2),
                "used_bytes": mem.used,
                "used_gb": round(mem.used / (1024 ** 3), 2),
                "percent_used": mem.percent
            }
        mem_data = run_with_timeout(collect_memory)
        if not mem_data.get("__skip"):
            result["memory"] = mem_data
        else:
            result["memory"] = mem_data

    # ========== 5. 磁盘信息 ==========
    if enable_disks:
        def collect_disk():
            disks = []
            for part in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    disks.append({
                        "device": part.device,
                        "mountpoint": part.mountpoint,
                        "fstype": part.fstype,
                        "total_gb": round(usage.total / (1024 ** 3), 2),
                        "used_gb": round(usage.used / (1024 ** 3), 2),
                        "free_gb": round(usage.free / (1024 ** 3), 2),
                        "percent_used": usage.percent
                    })
                except PermissionError:
                    disks.append({"mountpoint": part.mountpoint, "warning": "权限不足无法读取"})
            return disks
        disk_data = run_with_timeout(collect_disk)
        if not disk_data.get("__skip"):
            result["disks"] = disk_data
        else:
            result["disks"] = disk_data

    # ========== 6. 显卡信息 ==========
    if enable_gpus:
        def collect_gpu():
            gpus = []
            if platform.system() == "Windows":
                try:
                    import wmi
                    c = wmi.WMI()
                    for gpu in c.Win32_VideoController():
                        ram_raw = getattr(gpu, "AdapterRAM", None)
                        vram_gb = None
                        if ram_raw is not None:
                            ram_val = int(ram_raw)
                            if ram_val < 0:
                                ram_val += 2 ** 32
                            vram_gb = round(ram_val / (1024 ** 3), 2)
                        gpus.append({
                            "name": gpu.Name,
                            "driver_version": gpu.DriverVersion,
                            "vram_gb": vram_gb
                        })
                except ImportError:
                    gpus.append({"note": "Windows读取显卡需要安装 wmi"})
            elif platform.system() == "Linux":
                try:
                    out = subprocess.check_output(["lspci", "-nn"], text=True, stderr=subprocess.STDOUT)
                    for line in out.splitlines():
                        if "VGA" in line or "3D" in line or "Display" in line:
                            gpus.append({"raw": line.strip()})
                except Exception:
                    gpus.append({"note": "lspci 读取失败"})
            elif platform.system() == "Darwin":
                try:
                    out = subprocess.check_output(["system_profiler", "SPDisplaysDataType", "-json"], text=True)
                    gpus = json.loads(out).get("SPDisplaysDataType", [])
                except Exception:
                    gpus.append({"note": "macOS system_profiler读取失败"})
            return gpus
        gpu_data = run_with_timeout(collect_gpu)
        if not gpu_data.get("__skip"):
            result["gpus"] = gpu_data
        else:
            result["gpus"] = gpu_data

    # ========== 7. 当前进程信息 ==========
    if enable_process:
        def collect_process():
            proc = psutil.Process(os.getpid())
            return {
                "pid": proc.pid,
                "create_time": proc.create_time(),
                "rss_mb": round(proc.memory_info().rss / (1024 * 1024), 2),
                "vms_mb": round(proc.memory_info().vms / (1024 * 1024), 2),
                "cpu_percent": proc.cpu_percent(interval=0.05),
                "thread_count": len(proc.threads())
            }
        proc_data = run_with_timeout(collect_process)
        if not proc_data.get("__skip"):
            result["process"] = proc_data
        else:
            result["process"] = proc_data

    # ===================== Print模式：控制台打印输出 =====================
    if mode == "print":
        print("=" * 60)
        if "os" in result:
            osd = result["os"]
            if osd.get("__skip"):
                print(f"{lang['title_os']}: {osd['msg']}")
            else:
                print(f"【{lang['title_os']}】")
                print(f"  {lang['system']}: {osd['system']}")
                print(f"  {lang['release']}: {osd['release']}")
                print(f"  {lang['version']}: {osd['version']}")
                print(f"  {lang['machine']}: {osd['machine']}")
                print(f"  {lang['arch']}: {osd['arch']}")
                print(f"  {lang['node']}: {osd['node']}")
            print()

        if "python" in result:
            pyd = result["python"]
            if pyd.get("__skip"):
                print(f"{lang['title_python']}: {pyd['msg']}")
            else:
                print(f"【{lang['title_python']}】")
                print(f"  {lang['python_version']}: {pyd['version']}")
                print(f"  {lang['executable']}: {pyd['executable']}")
                print(f"  {lang['pip_version']}: {pyd['pip_version']}")
                if "installed_packages" in pyd:
                    print(f"  {lang['installed_packages']}: 已加载")
            print()

        if "cpu" in result:
            cpud = result["cpu"]
            if cpud.get("__skip"):
                print(f"{lang['title_cpu']}: {cpud['msg']}")
            else:
                print(f"【{lang['title_cpu']}】")
                print(f"  {lang['brand']}: {cpud['brand']}")
                print(f"  {lang['physical_cores']}: {cpud['physical_cores']}")
                print(f"  {lang['logical_cores']}: {cpud['logical_cores']}")
                print(f"  {lang['cpu_freq_current']}: {cpud['cpu_freq_current']}")
                print(f"  {lang['cpu_freq_max']}: {cpud['cpu_freq_max']}")
                print(f"  {lang['cpu_usage_total']}: {cpud['cpu_usage_total']}")
            print()

        if "memory" in result:
            memd = result["memory"]
            if memd.get("__skip"):
                print(f"{lang['title_memory']}: {memd['msg']}")
            else:
                print(f"【{lang['title_memory']}】")
                print(f"  {lang['total_gb']}: {memd['total_gb']}")
                print(f"  {lang['available_gb']}: {memd['available_gb']}")
                print(f"  {lang['used_gb']}: {memd['used_gb']}")
                print(f"  {lang['percent_used']}: {memd['percent_used']}")
            print()

        if "disks" in result:
            diskd = result["disks"]
            if diskd.get("__skip"):
                print(f"{lang['title_disks']}: {diskd['msg']}")
            else:
                print(f"【{lang['title_disks']}】")
                for part in diskd:
                    print(f"  {lang['mountpoint']}: {part['mountpoint']}, {lang['total_gb']}: {part['total_gb']} GB")
            print()

        if "gpus" in result:
            gpusd = result["gpus"]
            if gpusd.get("__skip"):
                print(f"{lang['title_gpus']}: {gpusd['msg']}")
            else:
                print(f"【{lang['title_gpus']}】")
                for gpu in gpusd:
                    print(f"  {lang['gpu_name']}: {gpu.get('name')}, {lang['vram_gb']}: {gpu.get('vram_gb')}")
            print()

        if "process" in result:
            procd = result["process"]
            if procd.get("__skip"):
                print(f"{lang['title_process']}: {procd['msg']}")
            else:
                print(f"【{lang['title_process']}】")
                print(f"  {lang['pid']}: {procd['pid']}")
                print(f"  {lang['rss_mb']}: {procd['rss_mb']}")
                print(f"  {lang['vms_mb']}: {procd['vms_mb']}")
                print(f"  {lang['process_cpu_percent']}: {procd['cpu_percent']}")
                print(f"  {lang['thread_count']}: {procd['thread_count']}")
            print()
        print("=" * 60)
        return None
    else:
        # get模式 返回字典
        return result


if __name__ == "__main__":
    # 示例1：打印模式，直接控制台输出，中文
    get_system_and_env_info(
        mode="print",
        python_fetch_pip_packages=False,
        timeout=3.0
    )

    # 示例2：get模式，返回JSON字典，英文语言包（仅print模式生效）
    # info = get_system_and_env_info(
    #     mode="get",
    #     enable_disks=False,
    #     enable_gpus=False,
    #     python_fetch_pip_packages=False,
    #     timeout=3.0,
    #     language="en-US"
    # )
    # json_str = json.dumps(info, indent=2, ensure_ascii=False)
    # print(json_str)
    # with open("system_debug_info.json", "w", encoding="utf-8") as f:
    #     json.dump(info, f, indent=2, ensure_ascii=False)
