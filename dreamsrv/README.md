# dreamsrv

> Server monitoring and control library for Python.

[![PyPI version](https://img.shields.io/pypi/v/dreamsrv.svg)](https://pypi.org/project/dreamsrv/)
[![Python versions](https://img.shields.io/pypi/pyversions/dreamsrv.svg)](https://pypi.org/project/dreamsrv/)
[![License](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](LICENSE)
[![Telegram](https://img.shields.io/badge/telegram-@devuranium-blue.svg)](https://t.me/devuranium)

**dreamsrv** is a lightweight, dependency-minimal Python library for monitoring and controlling Linux servers. It wraps `psutil` and `subprocess` into a clean, Pythonic API — so you can grab CPU load, memory usage, disk stats, network metrics, process lists, file contents, and run shell commands from a single `Server` object.

Built for server-side automation, Telegram userbots (Hikka), monitoring dashboards, and anything that needs to peek at the host it runs on.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [CPU](#cpu)
  - [Memory](#memory)
  - [Disk](#disk)
  - [Network](#network)
  - [Processes](#processes)
  - [Files](#files)
  - [System](#system)
  - [Shell Commands](#shell-commands)
- [Async Usage](#async-usage)
- [Hikka Module](#hikka-module)
- [Requirements](#requirements)
- [License](#license)

---

## Installation

```bash
pip install dreamsrv
