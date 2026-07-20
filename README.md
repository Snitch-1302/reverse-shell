# reverse-shell

A Python implementation of a reverse shell - built to understand offensive
network communication and command-and-control mechanics from first
principles, using raw sockets rather than a higher-level framework.

> **⚠️ Authorized use only.** This project is for educational purposes and
> authorized security testing (e.g. CTFs, your own lab environment, or
> engagements you're explicitly authorized to test) only. Using this
> against systems you don't own or don't have explicit permission to test
> is illegal. The techniques here are the same ones used by real malware
> for command-and-control - understanding them defensively (how to detect
> and respond to this kind of traffic) is the intended takeaway.

## What this is

A reverse shell attack works by having the compromised machine (the
**client**, here) initiate an outbound connection back to the attacker's
machine (the **server**), rather than the attacker connecting inbound -
this is what lets it slip past firewalls that block inbound connections
but allow outbound ones. Once connected, the server can send shell
commands to the client and receive their output, effectively getting
remote control.

This implementation supports:
- Multiple simultaneous client connections (up to 5 queued)
- A `list` / `select` interface on the server side to choose which
  connected client to control
- Automatic reconnection on the client side if the connection drops
- Multithreading on the server: one thread accepts incoming connections,
  a second handles the interactive command prompt

## Tech stack

- Python 3.x
- `socket` - raw TCP communication between client and server
- `threading` - concurrent connection-accepting and command-prompt handling
- `subprocess` - executing shell commands on the client and capturing output
- `queue` - coordinating the server's worker threads

## Project structure

```
reverse-shell/
├── client.py   # runs on the target machine; connects out to the server
├── server.py   # runs on the attacker machine; accepts connections, sends commands
└── README.md
```

## Setup

No external dependencies - both files use only Python's standard library.

1. In `client.py`, set `host` to the IP address of the machine running `server.py`
2. Both files use port `9999` by default - change consistently in both if needed

## Running it

**On the "attacker" machine:**
```bash
python server.py
```

**On the "target" machine:**
```bash
python client.py
```

Once connected, on the server side:

```
rshell> list                    # shows all connected clients
rshell> select 0                # selects client at index 0
127.0.0.1> whoami                # runs a command on that client, shows output
127.0.0.1> quit                  # returns to the rshell> prompt
```

## What I learned / what I'd improve

Building and debugging this surfaced two real bugs worth understanding, not just the "happy path" of getting a shell to connect:

**1. Infinite recursion instead of a loop.** The original `client.py` had `main()` call itself again at the very end, unconditionally - not just after an error. Since each call is a new stack frame rather than a loop iteration, this would eventually hit Python's recursion limit and crash with a `RecursionError` after enough reconnect attempts, instead of running indefinitely the way the logic seemed to intend. Fixed by replacing the recursive self-call with a `while True:` loop - same "keep retrying" behavior, no stack growth.

**2. Mutating a list while iterating over it.** `list_connections()` on the server deleted dead connections from `all_connections`/`all_addresses` while iterating over `enumerate(all_connections)` in the same loop. Deleting mid-iteration shifts every later index down by one, which can cause the loop to skip checking the very next connection. I proved this concretely: with two *consecutive* dead connections, the original logic only removed one of them, leaving a stale dead connection listed as active. Fixed by collecting dead indices first, then removing them afterward in reverse order.

**3. An unhandled `EOFError` on closed stdin.** If the server's input stream closes (e.g. `Ctrl+D`, or in my own testing, a finite piped input source running out), `input()` raises `EOFError`, which wasn't caught anywhere - crashing the whole prompt thread with a traceback. Fixed by catching `EOFError` around both `input()` calls and exiting the prompt loop cleanly instead.

I verified all three fixes by actually running the client and server against each other over a real local socket connection - not just reasoning about the code - including deliberately reproducing the exact crash scenarios before and after each fix to confirm the behavior actually changed.

Things I'd still improve with more time:
- Encrypt the command channel (currently plaintext TCP - trivially visible to anyone monitoring the network)
- Replace bare exception handling with more specific exception types throughout
- Make host/port configurable via command-line arguments instead of hardcoded constants

## Known limitations

- Command channel is unencrypted plaintext - visible to network monitoring
- No authentication between client and server - any client that connects to the configured port is accepted
- Host/port are hardcoded constants rather than configurable at runtime

## Full write-up

The two real bugs, how I found and proved them, and the authorized-use context in more depth: https://quietbytes.hashnode.dev/reverse-shell-python-debugging-three-bugs

