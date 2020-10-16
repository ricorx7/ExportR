from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
import qdarkstyle

from . import Exportr_view


class ExportrVM(Exportr_view.Ui_ExporterView):
    """
    ExportR to export raw data to other formats.
    """

    def __init__(self, parent):
        Exportr_view.Ui_ExporterView.__init__(self)
        self.setupUi(parent)
        self.parent = parent

        self.selected_files = []

        self.revLabel.setText("© Rowe Technologies Inc. Rev 1.0")

        self.selectFilesButton.clicked.connect(self.select_files)
        self.darkCheckBox.clicked.connect(self.change_theme)

    def select_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self.parent,
                                                "File Export",
                                                "",
                                                "Ensemble Files (*.ens, *.bin);;Binary Files (*.bin);;All Files (*)",
                                                options=options)
        if files:
            print(files)
            self.selected_files = files

            index = 0
            for file in self.selected_files:
                self.filesListWidget.insertItem(index, file)
                index += 1

    def change_theme(self):
        """
        Change the theme color.
        :return:
        """
        # get the QApplication instance,  or crash if not set
        app = QtWidgets.QApplication.instance()
        if app is None:
            raise RuntimeError("No Qt Application found.")

        if self.darkCheckBox.isChecked():
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        else:
            app.setStyleSheet("")
