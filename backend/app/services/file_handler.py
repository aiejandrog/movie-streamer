def get_video_duration(file_path: str) -> int | None:
    try:
        from mutagen import File as MutagenFile
        f = MutagenFile(file_path)
        if f and f.info:
            return int(f.info.length)
    except Exception:
        pass
    return None
