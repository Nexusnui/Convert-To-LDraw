# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ConvertToLDraw\\app.py'],
    pathex=[],
    binaries=[],
    datas=[('ConvertToLDraw\\icons\\ConvertToLDraw_icon.ico','icons'),
           ('ConvertToLDraw\\icons\\reload-icon.svg','icons'),
           ('ConvertToLDraw\\icons\\reload-icon.svg','ConvertToLDraw\\icons'),
           ('ConvertToLDraw\\brick_data\\colour_definitions.csv','ConvertToLDraw\\brick_data'),
           ('LICENSE','.'),
           ('ConvertToLDraw\\ui_elements\\viewer_template.html','ConvertToLDraw\\ui_elements'),
           ('ConvertToLDraw\\ui_elements\\js-libraries\\*.js','ConvertToLDraw\\ui_elements\\js-libraries')
           ],
    hiddenimports=[],
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
