# Wyoh development-only MCP bridge

`wyoh_mcp_server.py` maps every Sway 1.10 IPC request and subscription event
to named MCP stdio tools. It is not a product service and must be launched only
with `--full-ipc-development`; it starts and owns a disposable headless Sway
child and rejects ambient `SWAYSOCK`/`I3SOCK` variables.

The sole Python dependency is pinned in `requirements-mcp-over-ssh.txt`:
`mcp==2.2.0`. On `luna-pi`, the validation uses the isolated developer venv
`/home/michael/.local/opt/wyoh-mcp-2.2.0`, not the system Python environment.

The live test transfers this versioned source to that venv and launches it as
an SSH stdio child. It creates no listener, port-forward, persistent process,
or Luna change.
