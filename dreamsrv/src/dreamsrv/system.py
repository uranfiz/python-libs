import os
import platform
import time
import sys
import psutil
from .utils import seconds_to_readable

class System:
    """system information"""

    @property
    def uptime(self) -> str:
        """uptime as human-readable string"""
        return seconds_to_readable(int(time.time() - psutil.boot_time()))

    @property
    def hostname(self) -> str:
        """hostname"""
        return platform.node()

    @property
    def kernel(self) -> str:
        """kernel version"""
        return platform.release()

    @property
    def arch(self) -> str:
        """architecture"""
        return platform.machine()

    @property
    def os_name(self) -> str:
        """OS name (pretty)"""
        if hasattr(platform, "freedesktop_os_release"):
            try:
                return platform.freedesktop_os_release().get("PRETTY_NAME", platform.system())
            except Exception:
                pass
        return f"{platform.system()} {platform.release()}"

    @property
    def virtualization(self) -> str:
        """detect virtualization type"""
        if os.path.exists("/.dockerenv"):
            return "Docker"
        if os.path.exists("/run/systemd/container"):
            return "LXC"
        if os.path.exists("/proc/xen"):
            return "Xen"
        return "VPS / Bare Metal"

    @property
    def users(self) -> list[str]:
        """list of logged-in users"""
        try:
            return list({u.name for u in psutil.users()})
        except Exception:
            return []

    @property
    def python(self) -> str:
        """python version"""
        v = sys.version_info
        return f"{v.major}.{v.minor}.{v.micro}"
