from dataclasses import dataclass
import psutil
@dataclass
class ProcessInfo:
    pid: int
    name: str
    cpu: float
    mem: float

class Processes:
    """process metrics"""

    @property
    def count(self) -> int:
        """Total number of processes"""
        return len(psutil.pids())

    def get(self, pid: int) -> psutil.Process | None:
        """get a process by PID"""
        try:
            return psutil.Process(pid)
        except psutil.NoSuchProcess:
            return None

    def top_cpu(self, n: int = 5) -> list[ProcessInfo]:
        """top-N processes by CPU usage"""
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                info = p.info
                procs.append(ProcessInfo(
                    pid=info["pid"],
                    name=info["name"] or "?",
                    cpu=info["cpu_percent"] or 0.0,
                    mem=info["memory_percent"] or 0.0,
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        procs.sort(key=lambda x: x.cpu, reverse=True)
        return procs[:n]

    def top_mem(self, n: int = 5) -> list[ProcessInfo]:
        """top-N processes by memory usage"""
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                info = p.info
                procs.append(ProcessInfo(
                    pid=info["pid"],
                    name=info["name"] or "?",
                    cpu=info["cpu_percent"] or 0.0,
                    mem=info["memory_percent"] or 0.0,
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        procs.sort(key=lambda x: x.mem, reverse=True)
        return procs[:n]

    def kill(self, pid: int) -> bool:
        """kill a process by PID. Returns True on success"""
        try:
            psutil.Process(pid).kill()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
