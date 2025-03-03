import sys
from PyQt5.QtWidgets import QApplication

from directory_utils.directory_exploration import ScansExplorer


def run_app():
    app = QApplication(sys.argv)
    explorer = ScansExplorer()
    explorer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()
