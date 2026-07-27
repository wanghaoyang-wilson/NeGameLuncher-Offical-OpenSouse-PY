from UI import *
import cmd_model
import enumList
import argparse
import res_text
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = LuncherUI()
    win.show()
    sys.exit(app.exec())
