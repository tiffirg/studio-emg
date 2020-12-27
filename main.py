import sys
from PyQt5.QtWidgets import QApplication
from GUI import App


def main():
    app = QApplication(sys.argv)
    ex = App()
    ex.showMaximized()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
