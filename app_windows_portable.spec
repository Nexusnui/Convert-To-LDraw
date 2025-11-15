# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas=[('ThreeDToLD\\icons\\3DToLD_icon.ico','icons'),
           ('ThreeDToLD\\icons\\reload-icon.svg','icons'),
           ('ThreeDToLD\\icons\\reload-icon.svg','ThreeDToLD\\icons'),
           ('ThreeDToLD\\icons\\loading_animation.webm','icons'),
           ('ThreeDToLD\\icons\\Loading_Symbol.png','icons'),
           ('ThreeDToLD\\brick_data\\colour_definitions.csv','ThreeDToLD\\brick_data'),
           ('LICENSE','.'),
           ('ThreeDToLD\\ui_elements\\viewer_template.html','ThreeDToLD\\ui_elements'),
           ('ThreeDToLD\\ui_elements\\js-libraries\\*','ThreeDToLD\\ui_elements\\js-libraries')
]
datas += collect_data_files('collada')
datas += collect_data_files('trimesh')
datas += collect_data_files('lxml')
datas += collect_data_files('jsonschema_specifications')

a = Analysis(
    ['ThreeDToLD\\app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['cascadio', 'manifold3d', 'networkx', 'pillow', 'pycollada'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='3DToLD Portable',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ThreeDToLD\\icons\\3DToLD_icon.ico',
)
