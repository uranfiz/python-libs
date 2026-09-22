import psutil
from .utils import bytes_to_human

class Disk:
    """disk usage and I/O"""

    def used(self, path: str = "/") -> float:
        """used space in MB"""
        return psutil.disk_usage(path).used / (1024 ** 2)

    def total(self, path: str = "/") -> float:
        """total space in MB"""
        return psutil.disk_usage(path).total / (1024 ** 2)

    def free(self, path: str = "/") -> float:
        """free space in MB"""
        return psutil.disk_usage(path).free / (1024 ** 2)

    def percent(self, path: str = "/") -> float:
        """disk usage percentage"""
        return psutil.disk_usage(path).percent

    def used_human(self, path: str = "/") -> str:
        """used space in human-readable format"""
        return bytes_to_human(psutil.disk_usage(path).used)

    def total_human(self, path: str = "/") -> str:
        """total space in human-readable format"""
        return bytes_to_human(psutil.disk_usage(path).total)

    def free_human(self, path: str = "/") -> str:
        """free space in human-readable format"""
        return bytes_to_human(psutil.disk_usage(path).free)

    @property
    def io(self):
        """disk I/O counters"""
        return psutil.disk_io_counters()

    @property
    def partitions(self) -> list:
        """list of disk partitions"""
        return psutil.disk_partitions()
