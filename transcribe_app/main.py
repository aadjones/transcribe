# transcribe_app/main.py

import sys
from PySide6.QtWidgets import QApplication
from transcribe_app.gui import MainWindow

def main():
    print("Starting application...")  # Debug line
    app = QApplication(sys.argv)
    window = MainWindow()  # Assume MainWindow is defined in gui.py
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
