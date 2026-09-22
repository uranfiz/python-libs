"""
dreamsrv — Server monitoring and control library.

Usage:
    from dreamsrv import Server
    s = Server()
    print(s.cpu.load)
    print(s.mem.percent)
    print(s.run("df -h").stdout)
"""

from .server import Server

__version__ = "0.1.1"
__all__ = ["Server"]
