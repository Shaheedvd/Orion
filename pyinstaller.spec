# PyInstaller spec for packaging the FastAPI backend into a single EXE
# Note: Adjust datas to include data/ directory
from PyInstaller.utils.hooks import collect_submodules
block_cipher = None

a = Analysis(['app.py'],
             pathex=['.'],
             binaries=[],
             datas=[('data', 'data')],
             hiddenimports=collect_submodules('backend'),
             hookspath=[],
             runtime_hooks=[],
             excludes=[])
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='backend', debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False )
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name='backend')
