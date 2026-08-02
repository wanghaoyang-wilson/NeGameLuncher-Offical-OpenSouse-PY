def RFTxtLine(file_OJ,Index):
    try:
        file_OJ.seek(0)
        lines = file_OJ.readlines()
        if 0 <= Index < len(lines):
            return lines[Index].strip()
    except Exception:
        pass
    return ''
from pathlib import Path
from platformdirs import user_config_dir

def create_project_flat_directories(root_dir_name: str, *argv: str) -> list[Path]:
    # platformdirs 自动生成 系统配置目录/root_dir_name （仅此一层项目文件夹）
    project_root = Path(user_config_dir(root_dir_name))
    
    # 仅创建这个根目录，不会二次拼接名字
    project_root.mkdir(parents=True, exist_ok=True)

    created_list = [project_root]

    for dir_name in argv:
        # 禁止传入带分隔符的多级路径
        if any(sep in dir_name for sep in ("/", "\\", "..")):
            raise ValueError(f"非法文件夹名 {dir_name}，不支持递归多级路径")
        
        sub_dir = project_root / dir_name
        sub_dir.mkdir(exist_ok=True)
        created_list.append(sub_dir)

    return created_list
def create_file(file_path: str, content: str = '') -> None:
    file_path_obj = Path(file_path)
    file_path_obj.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path_obj, 'w', encoding='utf-8') as f:
        f.write(content)
def write_file(file_path: str, content: str) -> None:
    file_path_obj = Path(file_path)
    file_path_obj.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path_obj, 'w', encoding='utf-8') as f:
        f.write(content)
def read_file(file_path: str) -> str:
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        return ''
    with open(file_path_obj, 'r', encoding='utf-8') as f:
        return f.read()