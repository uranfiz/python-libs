import subprocess
from dataclasses import dataclass
@dataclass
class CommandResult:
    stdout: str
    stderr: str
    exit_code: int
    @property
    def ok(self) -> bool:
        return self.exit_code == 0

class Runner:
    """execute shell commands"""
    def run(self, cmd: str, timeout: int = 30) -> CommandResult:
        """execute a shell command. Returns stdout, stderr, exit_code"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return CommandResult(
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                stdout="",
                stderr=f"Command timed out after {timeout}s",
                exit_code=-1,
            )
        except Exception as e:
            return CommandResult(
                stdout="",
                stderr=str(e),
                exit_code=-1,
            )
