# transcribe_app/main.py

import sys

from PySide6.QtWidgets import QApplication

from transcribe_app.gui import MainWindow


def main():
    print("Starting application...")  # Debug line
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
