from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import logging
from rti_python.Writer.rti_netcdf import RtiNetcdf
from rti_python.Ensemble.Ensemble import Ensemble


class ExportNetCdfFileWorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    error
        `tuple` (exctype, value, traceback.format_exc() )

    ensemble_progress
        `int` Ensemble Number

    '''
    error = pyqtSignal(tuple)
    ensemble_progress = pyqtSignal(int)


class ExportNetCdfFileWorker(QThread):
    '''
    Worker thread

    Inherits from QThread to handler worker thread setup, signals and wrap-up.
    QThread was used over QRunnable because of the need for the event loop.

    Convert the file to netCDF.  Give progress to the GUI.

    '''

    def __init__(self, file_result, *args, **kwargs):
        super(ExportNetCdfFileWorker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.file_result = file_result
        self.args = args
        self.kwargs = kwargs
        self.signals = ExportNetCdfFileWorkerSignals()

    @pyqtSlot()
    def run(self):
        """
        Export the file to netCDF.  Ensure you analyze the file first
        go know how many ensemble pairs there are and the delta time
        between ensembles.

        :return:
        :rtype:
        """
        # Export the file
        logging.debug("Starting Export netCDF: " + self.file_result["FilePath"])
        net_cdf = RtiNetcdf()
        net_cdf.ensemble_progress_event += self.ensemble_progress_handler
        file_path = self.file_result["FilePath"]                                # File Path

        # Ensure a value is given for the number of ensembles
        total_ensembles = self.file_result['EnsPairCount']
        if total_ensembles <= 0:
            total_ensembles = self.file_result['EnsCount']

        logging.debug("Exporting " + str(total_ensembles) + " to netCDF")

        ens_to_process = [0, total_ensembles]                                   # Start and stop ensemble
        ens_delta = self.file_result['EnsembleDeltaTime']                       # Time between ensembles
        net_cdf.export(file_path, ens_to_process, ens_delta)                    # Start exporting the data

        logging.debug("Exporting netCDF Complete: " + self.file_result["FilePath"])

    @pyqtSlot()
    def ensemble_progress_handler(self, sender, ens: Ensemble):
        """
        Emit the ensemble number to show progress in the processing.  Send the ensemble number.
        :param sender: NOT USED
        :type sender:
        :param ens: Ensemble being processed.
        :type ens: Ensemble
        :return:
        :rtype:
        """
        # Get the ensemble number
        ens_num = 0
        if ens.IsEnsembleData:
            ens_num = ens.EnsembleData.EnsembleNumber

        # Emit the signal of a new ensemble with the ensemble number.
        self.signals.ensemble_progress.emit(ens_num)
        logging.debug("Ensemble Processed: " + str(ens_num))
