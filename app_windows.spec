# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas=[('ConvertToLDraw\\icons\\ConvertToLDraw_icon.ico','icons'),
           ('ConvertToLDraw\\icons\\reload-icon.svg','icons'),
           ('ConvertToLDraw\\icons\\reload-icon.svg','ConvertToLDraw\\icons'),
           ('ConvertToLDraw\\icons\\loading_animation.webm','icons'),
           ('ConvertToLDraw\\brick_data\\colour_definitions.csv','ConvertToLDraw\\brick_data'),
           ('LICENSE','.'),
           ('ConvertToLDraw\\ui_elements\\viewer_template.html','ConvertToLDraw\\ui_elements'),
           ('ConvertToLDraw\\ui_elements\\js-libraries\\*','ConvertToLDraw\\ui_elements\\js-libraries')
]
datas += collect_data_files('collada')
datas += collect_data_files('trimesh')
datas += collect_data_files('lxml')
datas += collect_data_files('jsonschema_specifications')

a = Analysis(
    ['ConvertToLDraw\\app.py'],
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
    [],
    exclude_binaries=True,
    name='Convert to LDraw',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ConvertToLDraw\\icons\\ConvertToLDraw_icon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Convert To LDraw',
)
