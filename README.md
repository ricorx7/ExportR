# ExportR
Rowe Technologies Inc. Export software used to export our binary data files (RTB) to netCDF 4 using CF time.

The software is written in python and uses a QT user interface. This software will not screen any data.  The exported data is the raw data.

It is assumed that the data exported will be either 4 Beam data or 5 Beam data.  7 Beam data will not work with this software currently.  If you try to use 8 Beam data, it will merge the data.

This will only export to netCDF right now.  If you need any additional formats, we have another application to export the data to MAT, CSV, and PD0.
http://rowetechinc.com/batch_exporter/

The source code is derived from the code from :
https://github.com/mmartini-usgs/ADCPy

To run the application, run the mainwindow.py file.

# Testing the File
I used Panoply software to test my created netCDF files.
https://www.giss.nasa.gov/tools/panoply/download/

# Create Installer EXE
Windows

You will need to install MSVC 2015 redistribution.


Then add C:\Program Files (x86)\Windows Kits\10\Redist\ucrt\DLLs\x64 to environment PATH. Then the warning message about api-ms-win-crt-***.dll will disappear and all works correctly.

```javascript
venv\Scripts\pyinstaller.exe ExportR_installer_WIN.spec
```

# Compile QT5 .UI files OSX
pyuic5 -x file.ui -o file.py
Windows

python -m PyQt5.uic.pyuic -x filename.ui -o filename.py

C:\Users\XXX\AppData\Local\Programs\Python\Python35\Scripts\pyuic5.exe -x file.ui -o file.py