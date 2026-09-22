import psutil
from .utils import bytes_to_human

class Memory:
    """RAM and Swap metrics"""

    @property
    def used(self) -> float:
        """used RAM in MB"""
        return psutil.virtual_memory().used / (1024 ** 2)

    @property
    def total(self) -> float:
        """total RAM in MB"""
        return psutil.virtual_memory().total / (1024 ** 2)

    @property
    def percent(self) -> float:
        """RAM usage percentage"""
        return psutil.virtual_memory().percent

    @property
    def available(self) -> float:
        """available RAM in MB"""
        return psutil.virtual_memory().available / (1024 ** 2)

    @property
    def swap_used(self) -> float:
        """used Swap in MB"""
        return psutil.swap_memory().used / (1024 ** 2)

    @property
    def swap_total(self) -> float:
        """total Swap in MB"""
        return psutil.swap_memory().total / (1024 ** 2)

    @property
    def swap_percent(self) -> float:
        """swap usage percentage"""
        return psutil.swap_memory().percent

    @property
    def used_human(self) -> str:
        """used RAM in human-readable format"""
        return bytes_to_human(psutil.virtual_memory().used)

    @property
    def total_human(self) -> str:
        """total RAM in human-readable format"""
        return bytes_to_human(psutil.virtual_memory().total)

    @property
    def available_human(self) -> str:
        """available RAM in human-readable format"""
        return bytes_to_human(psutil.virtual_memory().available)
