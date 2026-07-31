from UI import *
import cmd_model
import enumList
import argparse
import res_text
def main(argv = None):
    app = QApplication(sys.argv)
    cursor_png = QPixmap("Local/img/mouse.png")
    main_cursor = QCursor(cursor_png,0,0)
    app.setOverrideCursor(main_cursor)
    win = LuncherUI()
    win.show()
    sys.exit(app.exec())
main()