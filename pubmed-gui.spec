# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

datas = [
    ("assets/icon.ico", "assets"),
    ("assets/icon.png", "assets"),
    ("nbib_to_ris_converter.ps1", "."),
    ("add_pubmed_urls.ps1", "."),
    ("merge_ris.ps1", "."),
    ("process_ris_files.ps1", "."),
    ("extract_urls_with_titles.ps1", "."),
]

a = Analysis(
    ["gui_entry.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "dnd", "windnd", "openpyxl", "excel_export",
        "citations", "export_enrich", "prisma_report", "user_settings",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="PubMed Reference Converter",
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
    icon="assets/icon.ico",
)
