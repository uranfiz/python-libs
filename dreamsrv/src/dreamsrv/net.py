import asyncio
import time
import psutil
from .utils import bytes_to_human

class Network:
    """network metrics and ping"""

    @property
    def sent(self) -> int:
        """total bytes sent"""
        return psutil.net_io_counters().bytes_sent

    @property
    def recv(self) -> int:
        """total bytes received"""
        return psutil.net_io_counters().bytes_recv

    @property
    def sent_human(self) -> str:
        """total bytes sent in human-readable format"""
        return bytes_to_human(psutil.net_io_counters().bytes_sent)

    @property
    def recv_human(self) -> str:
        """total bytes received in human-readable format"""
        return bytes_to_human(psutil.net_io_counters().bytes_recv)

    @property
    def connections(self) -> int:
        """number of active INET connections"""
        try:
            return len(psutil.net_connections(kind="inet"))
        except Exception:
            return 0

    async def ping(self, host: str = "1.1.1.1", port: int = 53, timeout: float = 2.0) -> float | None:
        """async TCP ping. Returns latency in ms or None on failure"""
        try:
            start = time.perf_counter()
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=timeout
            )
            latency = (time.perf_counter() - start) * 1000
            writer.close()
            await writer.wait_closed()
            return latency
        except Exception:
            return None
