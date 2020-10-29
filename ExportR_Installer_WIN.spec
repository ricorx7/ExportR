# -*- mode: python -*-

block_cipher = None


a = Analysis(['mainwindow.py'],
             pathex=['C:\\Users\\rico\\Documents\\rti_code\\python\\ExportR\\venv\\Lib\\site-packages\\PyQt5\\Qt\\bin', 'C:\\Users\\rico\\Documents\\rti_code\\python\\ExportR', 'C:\\Users\\rico\\Documents\\rti_code\\python\\ExportR\View' ,'C:\\Users\\rico\\Documents\\rti_code\\python\\ExportR\\rti_python'],
             binaries=[],
             datas=[('rti.ico', '.')],
             hiddenimports=['obsub', 'cftime'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='ExportR',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='rti.ico')