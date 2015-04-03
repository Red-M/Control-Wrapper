Control-Wrapper
===============
This is a wrapper that can control any sub-process you give it to be controllable via a TCP server.
It is intended for server admins to control a process on a server while still receiving terminal output.

Supported Platforms
===================
- Linux
- Windows

OSX is untested.

Use
===
Simply run the wrapper and configure the TCP server with the config file generated on first run.
The passwords for each process is reloaded before every request.
