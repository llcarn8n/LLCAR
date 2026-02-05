#!/usr/bin/env python3
"""
Setup script for LLCAR Video Processing Pipeline
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="llcar",
    version="1.0.0",
    description="Video processing pipeline with speaker diarization and multi-language transcription",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="LLCAR Team",
    author_email="",
    url="https://github.com/llcarn8n/LLCAR",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "ffmpeg-python==0.2.0",
        "openai-whisper==20231117",
        "faster-whisper==1.0.0",
        "pyannote.audio==3.1.1",
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
        "scikit-learn==1.3.2",
        "nltk==3.8.1",
        "summa==1.2.0",
        "gensim==4.3.2",
        "transformers>=4.35.0",
        "accelerate>=0.24.0",
        "regex==2023.10.3",
        "PyYAML==6.0.1",
        "python-dotenv==1.0.0",
        "tqdm==4.66.1",
        "colorlog==6.8.0",
        "pandas==2.1.3",
    ],
    extras_require={
        "whisperx": [
            "whisperx @ git+https://github.com/m-bain/whisperx.git",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "llcar=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Video",
    ],
    keywords="video transcription diarization speaker-recognition whisper nlp",
)
