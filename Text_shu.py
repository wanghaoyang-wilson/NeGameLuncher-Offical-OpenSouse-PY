import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def count_file_lines(file_path, skip_empty_line: bool = False):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            if skip_empty_line:
                lines = [line for line in f if line.strip()]
            else:
                lines = f.readlines()
            return len(lines)
    except UnicodeDecodeError:
        return None
    except PermissionError:
        return -1
    except Exception:
        return None


class LineCountGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("目录文件行数统计工具")
        self.root.geometry("950x620")

        self.file_data = []

        # 顶部路径区域
        frame_top = ttk.Frame(root, padding=5)
        frame_top.pack(fill=tk.X)
        ttk.Label(frame_top, text="目标目录:").pack(side=tk.LEFT)
        self.var_path = tk.StringVar()
        ttk.Entry(frame_top, textvariable=self.var_path, width=65).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(frame_top, text="选择目录", command=self.select_folder).pack(side=tk.LEFT)

        # 配置区域
        frame_cfg = ttk.LabelFrame(root, text="排除配置（多个使用英文逗号 , 分隔）", padding=6)
        frame_cfg.pack(fill=tk.X, padx=5, pady=5)

        # 第0行：排除后缀
        ttk.Label(frame_cfg, text="排除后缀:").grid(row=0, column=0, sticky="w", pady=3)
        self.var_ex_suffix = tk.StringVar(value=".exe,.dll,.bin,.png,.jpg,.pyc,.zip")
        ttk.Entry(frame_cfg, textvariable=self.var_ex_suffix, width=38).grid(row=0, column=1, padx=5)

        # 第1行：排除文件
        ttk.Label(frame_cfg, text="排除文件名:").grid(row=1, column=0, sticky="w", pady=3)
        self.var_ex_file = tk.StringVar(value="line_count_result.txt")
        ttk.Entry(frame_cfg, textvariable=self.var_ex_file, width=38).grid(row=1, column=1, padx=5)
        ttk.Button(frame_cfg, text="选择排除文件", command=self.pick_exclude_files).grid(row=1, column=2, padx=4)

        # 第2行：排除文件夹
        ttk.Label(frame_cfg, text="排除文件夹:").grid(row=2, column=0, sticky="w", pady=3)
        self.var_ex_dir = tk.StringVar(value=".git,node_modules,venv,__pycache__,build,dist")
        ttk.Entry(frame_cfg, textvariable=self.var_ex_dir, width=38).grid(row=2, column=1, padx=5)
        ttk.Button(frame_cfg, text="选择排除目录", command=self.pick_exclude_dirs).grid(row=2, column=2, padx=4)

        # 忽略空行
        self.var_skip_empty = tk.BooleanVar()
        ttk.Checkbutton(frame_cfg, text="忽略空行", variable=self.var_skip_empty).grid(row=0, column=3, padx=12)

        # 按钮栏
        frame_btn = ttk.Frame(root, padding=5)
        frame_btn.pack(fill=tk.X)
        ttk.Button(frame_btn, text="开始统计", command=self.start_scan).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame_btn, text="导出结果", command=self.export_result).pack(side=tk.LEFT, padx=2)
        self.var_info = tk.StringVar(value="就绪")
        ttk.Label(frame_btn, textvariable=self.var_info).pack(side=tk.RIGHT)

        # 结果表格
        frame_tree = ttk.Frame(root)
        frame_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll_y = ttk.Scrollbar(frame_tree)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(frame_tree, yscrollcommand=scroll_y.set, columns=("lines", "path"), show="headings")
        scroll_y.config(command=self.tree.yview)
        self.tree.heading("lines", text="行数")
        self.tree.heading("path", text="文件路径")
        self.tree.column("lines", width=80, anchor=tk.E)
        self.tree.column("path", width=840)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 底部汇总
        frame_sum = ttk.Frame(root, padding=5)
        frame_sum.pack(fill=tk.X)
        self.var_sum = tk.StringVar(value="文件总数：0 | 总行数：0")
        ttk.Label(frame_sum, textvariable=self.var_sum, font=("", 10, "bold")).pack(side=tk.LEFT)

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.var_path.set(path)

    def pick_exclude_files(self):
        """弹窗多选文件，提取文件名追加到排除文件名列表"""
        paths = filedialog.askopenfilenames(title="选择需要排除的文件")
        if not paths:
            return
        names = [os.path.basename(p) for p in paths]
        old_text = self.var_ex_file.get().strip()
        old_list = [x.strip() for x in old_text.split(",") if x.strip()] if old_text else []
        # 合并去重
        all_names = list(set(old_list + names))
        self.var_ex_file.set(",".join(all_names))

    def pick_exclude_dirs(self):
        """选择文件夹，提取文件夹名称加入排除目录"""
        path = filedialog.askdirectory(title="选择需要排除的文件夹")
        if not path:
            return
        dirname = os.path.basename(path)
        old_text = self.var_ex_dir.get().strip()
        old_list = [x.strip() for x in old_text.split(",") if x.strip()] if old_text else []
        all_dirs = list(set(old_list + [dirname]))
        self.var_ex_dir.set(",".join(all_dirs))

    def start_scan(self):
        root_dir = self.var_path.get().strip()
        if not os.path.isdir(root_dir):
            messagebox.showerror("错误", "请先选择有效目录！")
            return

        self.tree.delete(*self.tree.get_children())
        self.file_data.clear()
        self.var_info.set("正在扫描...")
        self.root.update()

        ex_suffix = [s.strip() for s in self.var_ex_suffix.get().split(",") if s.strip()]
        ex_files = [s.strip() for s in self.var_ex_file.get().split(",") if s.strip()]
        ex_dirs = [s.strip() for s in self.var_ex_dir.get().split(",") if s.strip()]
        skip_empty = self.var_skip_empty.get()

        total_lines = 0
        file_count = 0

        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in ex_dirs]
            for fname in filenames:
                if fname in ex_files:
                    continue
                _, ext = os.path.splitext(fname)
                if ext in ex_suffix:
                    continue

                fullpath = os.path.join(dirpath, fname)
                cnt = count_file_lines(fullpath, skip_empty)
                if cnt is None or cnt == -1:
                    continue

                self.tree.insert("", tk.END, values=(cnt, fullpath))
                self.file_data.append((cnt, fullpath))
                total_lines += cnt
                file_count += 1
                self.root.update()

        self.var_sum.set(f"文件总数：{file_count} | 总行数：{total_lines}")
        self.var_info.set("扫描完成")

    def export_result(self):
        if not self.file_data:
            messagebox.showinfo("提示", "暂无统计数据")
            return
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile="行数统计结果.txt"
        )
        if not save_path:
            return
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write("行数\t文件路径\n")
                for cnt, path in self.file_data:
                    f.write(f"{cnt}\t{path}\n")
                all_lines = sum(i[0] for i in self.file_data)
                f.write(f"\n文件总数:{len(self.file_data)}  总行数:{all_lines}\n")
            messagebox.showinfo("成功", "导出完成！")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))


if __name__ == "__main__":
    win = tk.Tk()
    app = LineCountGUI(win)
    win.mainloop()