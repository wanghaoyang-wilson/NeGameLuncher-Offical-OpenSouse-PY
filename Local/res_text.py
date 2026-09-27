import enumList

# =====================================================================
# res_text：主题 QSS 的加载与应用
# 原实现：只读 Local/dark.qss，且只作用于单个 page（深色模式无法铺满全局）。
# 现支持：DARK / LIGHT 两套主题，读取后由调用方应用到全局 QApplication。
# =====================================================================


def read_qss(theme) -> str:
    """按主题枚举读取 QSS 文本；未知主题返回空串。"""
    if theme == enumList.theme.DARK:
        path = "Local/dark.qss"
    elif theme == enumList.theme.LIGHT:
        path = "Local/light.qss"
    else:
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def sk(theme) -> str:
    """兼容旧调用名：返回主题 QSS 文本。"""
    return read_qss(theme)
