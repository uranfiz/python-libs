from .cpu import CPU
from .mem import Memory
from .disk import Disk
from .net import Network
from .processes import Processes
from .files import Files
from .system import System
from .runner import Runner, CommandResult

class Server:
    """
    Main entry point for dreamsrv.

    Usage:
        s = Server()
        print(s.cpu.load)
        print(s.mem.percent)
        print(s.disk.percent("/"))
        print(s.system.uptime)
        r = s.run("df -h")
        print(r.stdout)
    """

    def __init__(self):
        self.cpu = CPU()
        self.mem = Memory()
        self.disk = Disk()
        self.net = Network()
        self.processes = Processes()
        self.files = Files()
        self.system = System()
        self._runner = Runner()

    def run(self, cmd: str, timeout: int = 30) -> CommandResult:
        """execute a shell command"""
        return self._runner.run(cmd, timeout)
