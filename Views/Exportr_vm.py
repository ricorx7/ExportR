from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import qdarkstyle
import logging
import threading
import os
from . import AnalyzeFileWorker, ExportNetCdfFileWorker, Exportr_view
from rti_python.Writer.rti_netcdf import RtiNetcdf
from rti_python.Ensemble.Ensemble import Ensemble


class ExportrVM(Exportr_view.Ui_ExporterView, QWidget):
    """
    ExportR to export raw data to other formats.
    """

    # Create signals to use in the VM
    sig_update_file_progress = pyqtSignal(int)
    sig_update_file_size = pyqtSignal(int)
    sig_set_analyze_file_result = pyqtSignal(object)
    sig_analyze_complete = pyqtSignal()
    sig_ensemble_progress = pyqtSignal(int)
    sig_export_complete = pyqtSignal()

    def __init__(self, parent):
        Exportr_view.Ui_ExporterView.__init__(self)
        QWidget.__init__(self, parent)
        self.setupUi(parent)
        self.parent = parent

        self.selected_files = []

        self.revLabel.setText("© Rowe Technologies Inc. Rev 1.0")

        self.selectFilesButton.clicked.connect(self.select_files)
        self.darkCheckBox.clicked.connect(self.change_theme)
        self.exportButton.clicked.connect(self.export_files)

        # Init progress bars
        self.fileAnalyzeProgressBar.setValue(0)
        self.scanFilesProgressBar.setValue(0)
        self.file_bytes_read = 0

        # Create the object to process the files and convert to netCDF
        #self.net_cdf = RtiNetcdf()
        #self.net_cdf.file_progress_event += self.file_progress_handler

        # Store all the analyze results
        self.analzye_results = []

        # Keep track of the next index
        self.export_file_index = 0
        self.analyze_file_index = 0

        # Setup Signal connections
        self.sig_update_file_progress.connect(self.file_progress_sig_handler)
        self.sig_update_file_size.connect(self.file_size_sig_handler)
        self.sig_set_analyze_file_result.connect(self.analyze_result_sig_handler)
        self.sig_analyze_complete.connect(self.analyze_complete_sig_handler)
        self.sig_ensemble_progress.connect(self.export_ensemble_progress_sig_handler)
        self.sig_export_complete.connect(self.export_file_complete_sig_handler)

    def select_files(self):
        """
        Use the dialog box to select the files you would like to export.
        Then analyze all the files to determine what data is within the file.
        :return:
        :rtype:
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self.parent,
                                                "File Export",
                                                os.path.expanduser('~/'),
                                                "Ensemble Files (*.ens, *.bin);;Binary Files (*.bin);;All Files (*)",
                                                options=options)
        if files:
            # Store the list of results
            self.selected_files = files

            # Analyze the files
            self.analyze_files()

    def analyze_files(self):
        """
        Analyze all the files.  This will check for the number of
        ensemble and the start and stop date and time.  It will also
        get the delta time between ensembles.

        All the results are stored to a list.  The index of the results
        will be the same index as the list of file names.
        :return:
        :rtype:
        """
        # Reset the analyze file results
        self.analzye_results.clear()
        self.filesListWidget.clear()

        # Update the progress bar
        self.scanFilesProgressBar.setMaximum(len(self.selected_files))

        # Reset the index
        self.analyze_file_index = 0

        # Start the analyzing
        # This will start the thread
        # When this thread is complete, the signal will be emitted
        # A and new thread will be created and started
        # This is to prevent all the threads starting at once
        if len(self.selected_files) > 0:
            self.analyze_file(self.selected_files[0])

    def analyze_file(self, file_path: str):
        """
        Create a thread to analyze the file.
        :param file_path: File path to analyze.
        :type file_path: string
        :return:
        :rtype:
        """
        # Set the file currently working on
        self.fileScanLabel.setText(file_path)

        # Reset the progress bar
        self.fileAnalyzeProgressBar.setValue(0)
        self.file_bytes_read = 0

        # Create a thread worker to do analyze the file
        logging.debug("----------------------------------------------")
        logging.debug("Start Analyze Thread")
        analyze_thread = threading.Thread(target=self.analyze_file_thread, args=(file_path, ))
        analyze_thread.start()
        logging.debug("Analyze Thread Complete")
        logging.debug("----------------------------------------------")

    def analyze_file_thread(self, file_path):
        """
        Thread to process analyze a file.  This will then
        emit the results to the signal.  It will then emit a
        complete signal to start the next file or complete.
        :param file_path: File path to analyze.
        :type file_path: str
        :return:
        :rtype:
        """
        net_cdf = RtiNetcdf()
        net_cdf.file_progress_event += self.file_progress_event_handler
        result = net_cdf.analyze_file(file_path)

        # Emit the result
        self.sig_set_analyze_file_result.emit(result)

        # Emit that thread is complete to start next file or complete
        self.sig_analyze_complete.emit()

    def file_progress_event_handler(self, sender, bytes_read: int, total_size: int, file_name: str):
        """
        Receive the event. Then pass the event to signals so the GUI can be updated.
        :param sender: NOT USED
        :type sender:
        :param bytes_read: Bytes read from the file.
        :type bytes_read: int
        :param total_size: Total size of the file in bytes.
        :type total_size: int
        :param file_name: File name in progress.
        :type file_name: str
        :return:
        :rtype:
        """
        self.sig_update_file_size.emit(total_size)
        self.sig_update_file_progress.emit(bytes_read)

    @pyqtSlot()
    def analyze_complete_sig_handler(self):
        """
        Once a thread has completed, this handler will be called.
        Then start the next file thread.  This is to prevent running
        all the threads at one time.
        :return:
        :rtype:
        """
        # Move to the next file
        self.analyze_file_index += 1

        # Verify we can move to the next file
        if self.analyze_file_index < len(self.selected_files):
            self.analyze_file(self.selected_files[self.analyze_file_index])
        else:
            # Analyzing is complete, so make sure the progress bar is at the end
            self.scanFilesProgressBar.setValue(len(self.selected_files))

        logging.debug("Completed Analyze File Thread")
        logging.debug("----------------------------------------------")

    @pyqtSlot(object)
    def analyze_result_sig_handler(self, result):
        """
        Receive the results from analyzing the file.
        :param result: Dictionary containing the results.
        :type result: dictionary
        :return:
        :rtype:
        """
        index = self.filesListWidget.count()
        self.filesListWidget.insertItem(index, result['CompleteFileDesc'])

        # Add the results to the list
        self.analzye_results.append(result)

        # Update the progress bar
        self.fileAnalyzeProgressBar.setValue(self.fileAnalyzeProgressBar.maximum())
        self.scanFilesProgressBar.setValue(index + 1)

        logging.debug("Got Results of Analyze File")
        logging.debug("----------------------------------------------")

    @pyqtSlot(int)
    def file_progress_sig_handler(self, bytes_read: int):
        """
        Handler to Keep track of the bytes read for the current file.
        :param bytes_read: Bytes read from the file.
        :type bytes_read: int
        :return:
        :rtype:
        """
        # Increment the bytes read
        self.file_bytes_read += bytes_read

        # Update the progress bar
        self.fileAnalyzeProgressBar.setValue(self.file_bytes_read)

        logging.debug("Analyzing File Progress: " + str(self.file_bytes_read))

    @pyqtSlot(int)
    def file_size_sig_handler(self, file_size: int):
        """
        Handler to set the file size to monitor the file progress.
        :param file_size: Total bytes in the file.
        :type file_size: int
        :return:
        :rtype:
        """
        # Verify the maximum has been set for the progress bar
        if self.fileAnalyzeProgressBar.maximum() != file_size:
            self.fileAnalyzeProgressBar.setMaximum(file_size)

        logging.debug("Set File Size: " + str(file_size))

    def export_files(self):
        # Clear the progress bars
        self.scanFilesProgressBar.setValue(0)
        self.scanFilesProgressBar.setMaximum(len(self.analzye_results))

        # Reset the index to start the export process
        self.export_file_index = 0

        # Export the file
        # This will start the loop
        # When one thread is complete, a new one will be started
        if len(self.analzye_results) > 0:
            self.export_file(self.analzye_results[0])

    def export_file(self, file_result: dict):
        # Determine the file had data
        if "EnsCount" in file_result and file_result["EnsCount"] > 0:
            # Check netCDF is checked
            if self.netcdfCheckBox.isChecked():
                # Set the progress bar max and reset the progress bar
                self.fileAnalyzeProgressBar.setValue(0)
                self.fileAnalyzeProgressBar.setMaximum(file_result["EnsCount"])

                # Set the file name
                if "CompleteFileDesc" in file_result:
                    self.fileScanLabel.setText(file_result["CompleteFileDesc"])
                elif "FilePath" in file_result:
                    self.fileScanLabel.setText(file_result["FilePath"])

                # Create a thread worker to do analyze the file
                #export_worker = ExportNetCdfFileWorker.ExportNetCdfFileWorker(file_result)
                #export_worker.signals.ensemble_progress.connect(self.export_ensemble_progress_handler)
                #export_worker.finished.connect(self.export_file_complete_handler)
                #export_worker.start()
                logging.debug("----------------------------------------------")
                logging.debug("Export File netCDF Thread")
                export_thread = threading.Thread(target=self.export_file_thread, args=(file_result,))
                export_thread.start()
                logging.debug("Export File netCDF Thread Complete")
                logging.debug("----------------------------------------------")

    def export_file_thread(self, file_result: dict):
        # Export the file
        logging.debug("Starting Export netCDF: " + file_result["FilePath"])
        net_cdf = RtiNetcdf()
        net_cdf.ensemble_progress_event += self.ensemble_progress_handler

        # File Path
        file_path = file_result["FilePath"]

        # Ensure a value is given for the number of ensembles
        total_ensembles = file_result['EnsPairCount']
        if total_ensembles <= 0:
            total_ensembles = file_result['EnsCount']

        logging.debug("Exporting " + str(total_ensembles) + " to netCDF")

        # Start and stop ensemble
        ens_to_process = [0, total_ensembles]

        # Time between ensembles
        ens_delta = file_result['EnsembleDeltaTime']

        # Start exporting the data
        net_cdf.export(file_path, ens_to_process, ens_delta)

        # Emit that thread is complete to start next file or complete
        self.sig_export_complete.emit()

        logging.debug("Exporting netCDF Complete: " + file_result["FilePath"])

    def ensemble_progress_handler(self, sender, ens: Ensemble):
        """
        Emit that a ensemble was received.
        :param sender: NOT USED
        :type sender:
        :param ens: Ensemble received.
        :type ens: Ensemble
        :return:
        :rtype:
        """
        if ens.IsEnsembleData:
            self.sig_ensemble_progress.emit(ens.EnsembleData.EnsembleNumber)
        else:
            # Just emit that an ensemble was received if no ensemble is known
            self.sig_ensemble_progress.emit(0)

    @pyqtSlot()
    def export_file_complete_sig_handler(self):
        """
        As one thread completes, we will start another thread.
        This will prevent all the threads for each file running at the same time.
        :return:
        :rtype:
        """
        # Increment the index
        self.export_file_index += 1

        # Move the state
        self.scanFilesProgressBar.setValue(self.scanFilesProgressBar.value() + 1)

        # Check if we have exported all the files
        if self.export_file_index >= len(self.analzye_results):
            # Show a dialog box that everything is exported and complete
            QMessageBox.question(self.parent, "Export Complete", "All files have been exported.", QMessageBox.Ok)
        else:
            # Export the next file
            self.export_file(self.analzye_results[self.export_file_index])

    @pyqtSlot(int)
    def export_ensemble_progress_sig_handler(self, ens_num: int):
        """
        Set the progress the ensembles being processed in the progressbar.
        :param ens_num: Ensemble number.
        :type ens_num: int
        :return:
        :rtype:
        """
        logging.debug(str(ens_num))
        self.fileAnalyzeProgressBar.setValue(self.fileAnalyzeProgressBar.value() + 1)

    def change_theme(self):
        """
        Change the theme color.
        :return:
        """
        # get the QApplication instance,  or crash if not set
        app = QApplication.instance()
        if app is None:
            raise RuntimeError("No Qt Application found.")

        if self.darkCheckBox.isChecked():
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        else:
            app.setStyleSheet("")
