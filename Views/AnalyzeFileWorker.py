from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from rti_python.Writer.rti_netcdf import RtiNetcdf
import logging


class AnalyzeFileWorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` Dictionary containing the results of the file analysis

    progress
        `int` indicating % progress

    '''
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    file_size = pyqtSignal(int)
    file_progress = pyqtSignal(int)


class AnalyzeFileWorker(QThread):
    '''
    Worker thread

    Inherits from QThread to handler worker thread setup, signals and wrap-up.
    QThread was used over QRunnable because of the need for the event loop.

    Analyze the file and pass the results on through a signal.  Use signal to give
    progress.
    '''

    def __init__(self, file_path, *args, **kwargs):
        super(AnalyzeFileWorker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.file_path = file_path
        self.args = args
        self.kwargs = kwargs
        self.did_we_send_file_size = False
        self.signals = AnalyzeFileWorkerSignals()

    @pyqtSlot()
    def run(self):
        """
        Analyze all the files.  This will check for the number of
        ensemble and the start and stop date and time.  It will also
        get the delta time between ensembles.

        All the results are stored to a list.  The index of the results
        will be the same index as the list of file names.
        :return:
        :rtype:
        """
        # Analyze the file
        logging.debug("Start analyzing: " + self.file_path)
        net_cdf = RtiNetcdf()
        net_cdf.file_progress_event += self.file_progress_handler
        result = net_cdf.analyze_file(self.file_path)

        # Emit the result
        self.signals.result.emit(result)

        logging.debug("Completed analyzing: " + self.file_path)

    @pyqtSlot()
    def file_progress_handler(self, sender, bytes_read: int, total_size: int, file_name: str):
        """
        Emit the file progress to the GUI.
        :param sender: NOT USED
        :type sender:
        :param bytes_read: Bytes read.
        :type bytes_read: int
        :param total_size: Total size of the file.
        :type total_size: int
        :param file_name: File name being processed.
        :type file_name: str
        :return:
        :rtype:
        """
        if not self.did_we_send_file_size:
            self.signals.file_size.emit(total_size)
            self.did_we_send_file_size = True
            logging.debug("Send File Size: " + str(total_size) + " " + file_name)

        self.signals.file_progress.emit(bytes_read)
        logging.debug("File progress: " + str(bytes_read) + " " + file_name)
