About
=====
Python3 daemon module

Table of contents
=================

- [About](#about)
- [Installation](#installation)
- [Examples](#examples)
    - [Daemon](#daemon)
    - [Background process](#background-process)

Installation
============
```bash
pip3 install mydaemon
```

Examples
========

Daemon
------
See [sample Python script](/examples/myservice.py) which run as a service (daemon)

```bash
python3 myservice.py start
python3 myservice.py restart
python3 myservice.py stop
```

Background process
------------------
See [sample Python script](/examples/myproc.py) which run as a background process.
Use "stop" parameter to force to stop.

```bash
python3 myproc.py start 1
python3 myproc.py start 2
python3 myproc.py start 3
python3 myproc.py stop 2
```
