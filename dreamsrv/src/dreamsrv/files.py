import os
from pathlib import Path

class Files:
    """file operations"""

    def read(self, path: str, encoding: str = "utf-8") -> str | None:
        """read a file. Returns None on error"""
        try:
            return Path(path).read_text(encoding=encoding)
        except Exception:
            return None

    def write(self, path: str, data: str, encoding: str = "utf-8") -> bool:
        """write to a file. Returns True on success"""
        try:
            Path(path).write_text(data, encoding=encoding)
            return True
        except Exception:
            return False

    def tail(self, path: str, lines: int = 50, encoding: str = "utf-8") -> str | None:
        """return last N lines of a file"""
        try:
            with open(path, "r", encoding=encoding, errors="replace") as f:
                content = f.readlines()
            return "".join(content[-lines:])
        except Exception:
            return None

    def exists(self, path: str) -> bool:
        """check if path exists"""
        return os.path.exists(path)

    def list(self, path: str = ".") -> list[str]:
        """list directory contents"""
        try:
            return os.listdir(path)
        except Exception:
            return []

    def size(self, path: str) -> int | None:
        """get file size in bytes"""
        try:
            return os.path.getsize(path)
        except Exception:
            return None
