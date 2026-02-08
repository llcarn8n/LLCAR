"""
Supported File Formats
Defines all supported video and audio file extensions for the LLCAR pipeline.
"""

# Supported video formats
VIDEO_EXTENSIONS = {
    '.mp4': 'MPEG-4 Video',
    '.avi': 'Audio Video Interleave',
    '.mov': 'QuickTime Movie',
    '.mkv': 'Matroska Video',
    '.wmv': 'Windows Media Video',
    '.flv': 'Flash Video',
    '.webm': 'WebM Video',
    '.m4v': 'MPEG-4 Video',
    '.mpg': 'MPEG Video',
    '.mpeg': 'MPEG Video',
}

# Supported audio formats
AUDIO_EXTENSIONS = {
    '.wav': 'Waveform Audio File',
    '.mp3': 'MP3 Audio',
    '.flac': 'Free Lossless Audio Codec',
    '.ogg': 'Ogg Vorbis Audio',
    '.m4a': 'MPEG-4 Audio',
    '.wma': 'Windows Media Audio',
    '.aac': 'Advanced Audio Coding',
    '.opus': 'Opus Audio',
}

# Combined list of all supported extensions
ALL_EXTENSIONS = {**VIDEO_EXTENSIONS, **AUDIO_EXTENSIONS}


def is_video_file(file_path: str) -> bool:
    """
    Check if file is a supported video format.

    Args:
        file_path: Path to file

    Returns:
        True if file is a supported video format
    """
    from pathlib import Path
    ext = Path(file_path).suffix.lower()
    return ext in VIDEO_EXTENSIONS


def is_audio_file(file_path: str) -> bool:
    """
    Check if file is a supported audio format.

    Args:
        file_path: Path to file

    Returns:
        True if file is a supported audio format
    """
    from pathlib import Path
    ext = Path(file_path).suffix.lower()
    return ext in AUDIO_EXTENSIONS


def is_supported_file(file_path: str) -> bool:
    """
    Check if file is a supported format (video or audio).

    Args:
        file_path: Path to file

    Returns:
        True if file is supported
    """
    return is_video_file(file_path) or is_audio_file(file_path)


def get_file_type_description(file_path: str) -> str:
    """
    Get description of file type.

    Args:
        file_path: Path to file

    Returns:
        Description of file type or 'Unknown'
    """
    from pathlib import Path
    ext = Path(file_path).suffix.lower()
    return ALL_EXTENSIONS.get(ext, 'Unknown')
