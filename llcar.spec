# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for LLCAR Video Processing Pipeline

This file is used to build a standalone Windows executable.
Run: pyinstaller llcar.spec
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all data files
datas = [
    ('config.yaml', '.'),
    ('.env.example', '.'),
    ('README.md', '.'),
    ('LICENSE', '.'),
]

# Collect hidden imports
hiddenimports = [
    'src',
    'src.pipeline',
    'src.audio_extraction',
    'src.diarization',
    'src.transcription',
    'src.postprocessing',
    'src.output',
    'src.console',
    'torch',
    'torchaudio',
    'whisper',
    'pyannote.audio',
    'pyannote.core',
    'pyannote.database',
    'transformers',
    'accelerate',
    'sklearn',
    'sklearn.feature_extraction',
    'sklearn.feature_extraction.text',
    'nltk',
    'nltk.tokenize',
    'nltk.corpus',
    'summa',
    'summa.keywords',
    'gensim',
    'regex',
    'yaml',
    'dotenv',
    'tqdm',
    'colorlog',
    'pandas',
    'ffmpeg',
]

# Collect all submodules from key packages
hiddenimports += collect_submodules('torch')
hiddenimports += collect_submodules('transformers')
hiddenimports += collect_submodules('pyannote')
hiddenimports += collect_submodules('sklearn')
hiddenimports += collect_submodules('nltk')

# Collect data files from packages
datas += collect_data_files('torch')
datas += collect_data_files('torchaudio')
datas += collect_data_files('transformers')
datas += collect_data_files('pyannote')
datas += collect_data_files('nltk')
datas += collect_data_files('sklearn')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='llcar',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path here if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='llcar',
)
