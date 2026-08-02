# running.py 放在 D:\NeGameLuncher\ 根目录
import sys
from pathlib import Path

# 把Local文件夹加入系统路径，保证内部模块能正常import
base_dir = Path(__file__).parent
sys.path.insert(0, str(base_dir / "Local"))

# 导入真正的主程序并运行
if __name__ == "__main__":
    import main # pyright: ignore[reportMissingImports]
    main.main(sys.argv)