import os
import platform
import psutil

class CPU:
    """CPU metrics"""

    @property
    def load(self) -> float:
        """current CPU load percentage (non-blocking)"""
        return psutil.cpu_percent(interval=None)

    @property
    def load_per_core(self) -> list[float]:
        """per-core CPU load"""
        return psutil.cpu_percent(percpu=True, interval=None)

    @property
    def freq(self) -> float | None:
        """current frequency in MHz"""
        f = psutil.cpu_freq()
        return f.current if f else None

    @property
    def count_logical(self) -> int:
        """number of logical cores"""
        return psutil.cpu_count(logical=True) or 0

    @property
    def count_physical(self) -> int:
        """number of physical cores"""
        return psutil.cpu_count(logical=False) or 0

    @property
    def model(self) -> str:
        """CPU model name"""
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
        return platform.processor() or "Unknown"

    @property
    def load_avg(self) -> tuple[float, float, float] | None:
        """load average (1m, 5m, 15m) on Unix"""
        try:
            return os.getloadavg()
        except (OSError, AttributeError):
            return None

    @property
    def temp(self) -> float | None:
        """CPU temperature in Celsius, if sensors available"""
        try:
            temps = psutil.sensors_temperatures()
            if "coretemp" in temps:
                return temps["coretemp"][0].current
            if "cpu_thermal" in temps:
                return temps["cpu_thermal"][0].current
        except Exception:
            pass
        return None

    @property
    def times(self) -> dict:
        """CPU times: user, system, idle, etc"""
        t = psutil.cpu_times()
        return {
            "user": t.user,
            "system": t.system,
            "idle": t.idle,
        }
