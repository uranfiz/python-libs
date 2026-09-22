from dreamsrv import Server

def test_server_init():
    s = Server()
    assert s.cpu is not None
    assert s.mem is not None
    assert s.disk is not None
    assert s.net is not None
    assert s.processes is not None
    assert s.files is not None
    assert s.system is not None

def test_cpu():
    s = Server()
    assert isinstance(s.cpu.load, float)
    assert isinstance(s.cpu.count_logical, int)
    assert s.cpu.count_logical > 0
    assert isinstance(s.cpu.model, str)

def test_mem():
    s = Server()
    assert isinstance(s.mem.percent, float)
    assert 0 <= s.mem.percent <= 100
    assert s.mem.total > 0

def test_disk():
    s = Server()
    assert isinstance(s.disk.percent("/"), float)
    assert s.disk.total("/") > 0

def test_run():
    s = Server()
    r = s.run("echo hello")
    assert r.ok
    assert "hello" in r.stdout

def test_system():
    s = Server()
    assert isinstance(s.system.hostname, str)
    assert isinstance(s.system.uptime, str)
    assert isinstance(s.system.python, str)
