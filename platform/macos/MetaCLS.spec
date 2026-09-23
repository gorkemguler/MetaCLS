# Build from the repository root using platform/macos/build-drop-app.sh.
import os
from pathlib import Path
from importlib.metadata import version
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

root = Path(SPECPATH).parents[1]
identity = os.environ.get('MACOS_CODESIGN_IDENTITY') or None
app_version = version('metacls')
a = Analysis(
    [str(root / 'platform/macos/desktop_entry.py')],
    pathex=[str(root / 'platform/macos')],
    binaries=[],
    datas=collect_data_files('metacls') + copy_metadata('metacls') + [
        (str(root / 'build/vendor/exiftool-13.59/exiftool'), 'vendor/exiftool'),
        (str(root / 'build/vendor/exiftool-13.59/lib'), 'vendor/exiftool/lib'),
        (str(root / 'build/vendor/exiftool-13.59/README'), 'licenses/exiftool'),
        (str(root / 'build/vendor/exiftool-13.59/LICENSE'), 'licenses/exiftool'),
        (str(root / 'LICENSE'), 'licenses/metacls'),
        (str(root / 'build/macos/THIRD-PARTY-LICENSES.txt'), 'licenses'),
    ],
    hiddenimports=['AppKit', 'Foundation', 'PyObjCTools.AppHelper'],
    excludes=['tkinter', 'pytest', 'IPython', 'matplotlib', 'fastapi', 'uvicorn', 'extract_msg', 'py7zr'],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='MetaCLS Drop',
          debug=False, strip=False, upx=False, console=False,
          argv_emulation=False, target_arch=None, codesign_identity=identity)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='MetaCLS Drop')
app = BUNDLE(coll, name='MetaCLS Drop.app',
             icon=str(root / 'build/macos/MetaCLS.icns'),
             bundle_identifier='com.gorkemguler.metacls.drop',
             version=app_version,
             info_plist={
                 'CFBundleShortVersionString': app_version,
                 'LSMinimumSystemVersion': '14.0',
                 'NSHighResolutionCapable': True,
                 'LSApplicationCategoryType': 'public.app-category.utilities',
                 'CFBundleDocumentTypes': [{
                     'CFBundleTypeName': 'Documents and images',
                     'CFBundleTypeRole': 'Editor',
                     'LSHandlerRank': 'Alternate',
                     'LSItemContentTypes': ['public.data'],
                 }],
             })
