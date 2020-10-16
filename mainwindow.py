import sys

from PyQt5 import QtGui, QtWidgets

from Views.Exporter_vm import ExportrVM
import qdarkstyle
# import images_qr


class MainWindow(QtWidgets.QMainWindow):
    """
    Main window for the application
    """

    def __init__(self, config=None):
        QtWidgets.QMainWindow.__init__(self)

        # Initialize the pages
        self.predictor = ExportrVM(self)

        # Initialize the window
        self.main_window_init()

    def main_window_init(self):
        # Set the title of the window
        self.setWindowTitle("Rowe Technologies Inc. - ExportR")

        self.setWindowIcon(QtGui.QIcon(":rti.ico"))

        # Show the main window
        self.show()

    def closeEvent(self, event):
        """
        Generate 'question' dialog on clicking 'X' button in title bar.
        Reimplement the closeEvent() event handler to include a 'Question'
        dialog with options on how to proceed - Close, Cancel buttons
        """
        reply = QtWidgets.QMessageBox.question(self, "Message",
            "Are you sure you want to quit?", QtWidgets.QMessageBox.Close | QtWidgets.QMessageBox.Cancel)

        if reply == QtWidgets.QMessageBox.Close:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Mac")

    #app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    MainWindow()
    sys.exit(app.exec_())