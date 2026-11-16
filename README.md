# NetCrash V1.0

**Fast threaded TCP port scanner. Terminal only. English only.**

NetCrash is a fast, lightweight port scanner for authorized security testing. It finds open ports on a target, tells you what service is running on each one, and saves the result as a report.

Hack The Planet — https://hackthepalnte.co.uk

---

## What is NetCrash?

NetCrash is the updated version of the fast port scanner from AB-RECON.

The old scanner in AB-RECON (`ab_recon.py`) scanned only 10 common ports, one by one, with a 1-second timeout. That is a basic check, not a fast scan.

NetCrash rebuilds that idea properly:

- It scans with threads, so hundreds of ports are checked at the same time instead of one by one.
- It covers the full port range when you ask for it.
- It tells you the service on each open port and reads the service banner where one is available.
- It shows live progress and prints each open port the moment it is found.
- It saves a clean report you can keep or share.

NetCrash is a port scanner only. It does not do OSINT, vulnerability scanning, brute force, or exploitation. It answers one question, fast: **which ports are open on this target, and what is running on them?**

---

## Features

### Fast threaded scanning

NetCrash uses a thread pool (default 100 threads, up to 500). A full scan of all 65,535 ports finishes in seconds on a local network instead of minutes or hours with a sequential scan.

### Four scan modes

| Mode | Command | What it scans |
|---|---|---|
| Fast (default) | `netcrash 192.168.1.1` | Top 100 most common ports |
| Top 1000 | `--top1000` | Top 1000 most common ports |
| Full | `--full` | All ports, 1–65535 |
| Custom | `--ports 80,443,8000-8100` | Only the ports you list, single ports and ranges |

Only one mode can be used at a time. If you give no mode, NetCrash runs the Fast scan.

### Service detection

Every open port is shown with its service name, for example:

- 22 — SSH
- 80 — HTTP
- 443 — HTTPS
- 3306 — MySQL
- 3389 — RDP
- 5432 — PostgreSQL
- 5900 — VNC
- 8080 — HTTP-Proxy

NetCrash uses a built-in service list first, then falls back to the system service database. If a port has no known service, it is shown as `unknown`.

### Banner grabbing

Where a service sends a banner, NetCrash reads it and shows the first line (up to 80 characters). For HTTP-like ports it sends a `HEAD` request to get a response. Example: an open web server may show `HTTP/1.0 200 OK`.

Use `--no-banner` to skip banner grabbing.

### Live progress

While the scan runs, one progress line shows how many ports are done, the percentage, and how many open ports have been found so far. Open ports are printed immediately on their own line — you do not have to wait for the scan to finish to see them.

### Save a report

Save the result with `--output`:

- `--output report.txt` — plain text report, easy to read.
- `--output report.json` — JSON report, easy to use in other tools or scripts.

The report includes the tool version, target, IP address, scan mode, date and time, scan duration, number of open ports, and the full list of open ports with service and banner.

### Clean terminal output

NetCrash prints a red block banner once at the start, one short ethical-use warning, then the scan. It does not print step-by-step instructions on every command. Run it with no target and it shows the banner and the short usage line `netcrash example.com`. For full usage instructions, run one command:

```bash
netcrash --help
```

### No dependencies

NetCrash uses only the Python standard library. There is nothing to install with pip. It runs on any system with Python 3.8 or newer.

---

## Requirements

- Python 3.8 or newer
- No external libraries
- A terminal (Linux, macOS, or Windows)

Check your Python version:

```bash
python3 --version
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/hacktheplanet-official/NetCrash.git
cd NetCrash
```

Install the `netcrash` command (once):

```bash
chmod +x install.sh
./install.sh
```

That copies `netcrash.py` to `/usr/local/bin/netcrash`. There is no `pip install` step.

Then run it like nmap:

```bash
netcrash --help
netcrash example.com
```

Without installing, run it from the folder with `./netcrash.py example.com`.

---

## Quick start

Scan a target with the default Fast scan (top 100 ports):

```bash
netcrash 192.168.1.1
```

Scan a domain instead of an IP address (NetCrash resolves it first):

```bash
netcrash example.com
```

Scan everything and save a JSON report:

```bash
netcrash example.com --full --output report.json
```

---

## Usage in detail

### 1. Fast scan (default)

Top 100 most common ports. Best when you want a quick answer.

```bash
netcrash 192.168.1.1
netcrash 192.168.1.1 --fast
```

### 2. Top 1000 scan

Top 1000 most common ports. A good middle ground between speed and coverage.

```bash
netcrash 192.168.1.1 --top1000
```

### 3. Full scan

All ports from 1 to 65535. Use this when you do not want to miss an uncommon open port.

```bash
netcrash 192.168.1.1 --full
```

### 4. Custom ports

Scan only the ports you care about. You can mix single ports and ranges, separated by commas.

```bash
netcrash 192.168.1.1 --ports 80,443
netcrash 192.168.1.1 --ports 8000-8100
netcrash 192.168.1.1 --ports 22,80,443,8000-8100,3306
```

### 5. Control speed

More threads make the scan faster. A shorter timeout also makes it faster, but a timeout that is too short can miss slow services.

```bash
netcrash 192.168.1.1 --full --threads 200
netcrash 192.168.1.1 --full --threads 200 --timeout 1.0
```

- `--threads N` — default 100, allowed 1 to 500.
- `--timeout SECONDS` — default 0.5, allowed up to 10.

### 6. Save a report

```bash
netcrash 192.168.1.1 --full --output report.txt
netcrash example.com --top1000 --output report.json
```

### 7. Other options

```bash
netcrash --help       # Show full usage and examples
netcrash --version    # Show the version: NetCrash V1.0
netcrash 192.168.1.1 --no-banner   # Skip banner grabbing
netcrash 192.168.1.1 --no-color    # Plain output, no red colour
```

Press `Ctrl+C` at any time to stop a scan. NetCrash prints the partial results found so far.

---

## All options

| Option | What it does |
|---|---|
| `target` | Target IP address or domain name to scan |
| `--fast` | Scan top 100 common ports (default) |
| `--top1000` | Scan top 1000 common ports |
| `--full` | Scan all ports 1–65535 |
| `--ports 80,443,8000-8100` | Custom port list, ranges, or both |
| `--threads N` | Number of threads (default: 100, max: 500) |
| `--timeout SECONDS` | Connection timeout in seconds (default: 0.5) |
| `--output FILE` | Save report to file (`.txt` or `.json`) |
| `--no-banner` | Do not grab service banners |
| `--no-color` | Disable coloured output |
| `--version` | Show version and exit |
| `-h, --help` | Show help and examples, then exit |

---

## Example output

A scan against a local test server on port 8000:

```
 ███╗   ██╗███████╗████████╗ ██████╗██████╗  █████╗ ███████╗██╗  ██╗
 ████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║
 ██╔██╗ ██║█████╗     ██║   ██║     ██████╔╝███████║███████╗███████║
 ██║╚██╗██║██╔══╝     ██║   ██║     ██╔══██╗██╔══██║╚════██║██╔══██║
 ██║ ╚████║███████╗   ██║   ╚██████╗██║  ██║██║  ██║███████║██║  ██║
 ╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝

                    NetCrash V1.0
              Hack The Planet - hackthepalnte.co.uk

Only scan systems you own or have permission to test.

Target: 127.0.0.1 (127.0.0.1)
Mode: custom (8000,2222,9999)  |  Ports: 3  |  Threads: 100

[+] 8000   open  HTTP-Alt  HTTP/1.0 200 OK

PORT    SERVICE             BANNER
------------------------------------------------------------
8000    HTTP-Alt            HTTP/1.0 200 OK
------------------------------------------------------------
Done. 1 open port(s) out of 3 scanned in 0.01s.
```

The banner at the top is printed in full red in the terminal. If output is piped to a file, colour is turned off automatically.

---

## Example reports

### Text report (`--output report.txt`)

```
NetCrash V1.0 - Scan Report
Target: 127.0.0.1 (127.0.0.1)
Mode: custom (8000,2222,9999)
Date: 2026-11-17T00:30:20
Scan time: 0.01s
Open ports: 1
------------------------------------------------------------
PORT    SERVICE             BANNER
------------------------------------------------------------
8000    HTTP-Alt            HTTP/1.0 200 OK
```

### JSON report (`--output report.json`)

```json
{
  "tool": "NetCrash V1.0",
  "target": "127.0.0.1",
  "ip": "127.0.0.1",
  "mode": "custom (8000,2222,9999)",
  "scanned_at": "2026-11-17T00:30:20",
  "scan_time_seconds": 0.01,
  "open_ports": 1,
  "results": [
    {
      "port": 8000,
      "service": "HTTP-Alt",
      "banner": "HTTP/1.0 200 OK"
    }
  ]
}
```

---

## How it works

1. **Resolve the target.** A domain name is resolved to an IP address first. If it cannot be resolved, NetCrash stops with an error.
2. **Build the port list.** Based on the mode you picked: top 100, top 1000, full range, or your custom list.
3. **Scan with threads.** Each thread tries a TCP connection to one port with the timeout you set. A successful connection means the port is open. A refused connection or timeout means it is closed.
4. **Identify the service.** For each open port, NetCrash looks up the service name and, unless you used `--no-banner`, tries to read the service banner.
5. **Report.** Open ports print as they are found. At the end, NetCrash prints a table of all open ports, the total scanned, and the time taken. If you used `--output`, it also writes the report file.

---

## Speed

Tested on localhost (127.0.0.1) with the default 100 threads:

| Scan | Ports | Time |
|---|---|---|
| Fast | 100 | 0.02s |
| Top 1000 | 1000 | 0.08s |
| Full | 65535 | 5.53s |

Speed on a real target depends on the network, the target, the timeout, and the number of threads. A filtered or distant target is slower than localhost because more connections have to wait for the timeout. If a scan feels slow, lower the timeout or raise the thread count. If results look incomplete, raise the timeout instead.

---

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Scan finished |
| 2 | Usage error — bad port, bad option, or target could not be resolved |
| 130 | Scan stopped by the user (Ctrl+C) — partial results are shown |

---

## Common errors

**`Error: Port out of range: 99999`**

The port must be between 1 and 65535. Check the `--ports` value.

**`Error: Could not resolve 'example.com'. Check the address and try again.`**

The domain name could not be resolved. Check the spelling and your network connection.

**`error: Use only one of --fast, --top1000, --full or --ports.`**

Pick one scan mode at a time.

**`Error: --threads must be between 1 and 500.`**

Use a thread count from 1 to 500.

---

## Legal and ethical use

Only scan systems you own or have explicit permission to test. Port scanning a system without permission is illegal in many countries and can get your IP address blocked.

NetCrash is built for learning, for your own labs and home network, and for authorized security testing. The author is not responsible for misuse.

---

## About

- **Author:** Abdullah Balouch
- **Project:** Hack The Planet
- **Website:** https://hackthepalnte.co.uk
- **Version:** V1.0 — first public release, 17 November 2026

## Version history

- **V1.0 (17 November 2026)** — First release. Threaded fast scanner with Fast / Top 1000 / Full / Custom modes, service detection, banner grabbing, live progress, and TXT/JSON reports. Replaces the 10-port sequential scan from AB-RECON.
