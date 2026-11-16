# NetCrash V1.0

Fast threaded TCP port scanner. Terminal only. English only.

Hack The Planet - hackthepalnte.co.uk

## What it does

NetCrash is the updated version of the fast port scanner from AB-RECON. The old version scanned only 10 common ports, one by one. NetCrash scans with threads, so a full scan is fast.

- Fast scan: top 100 common ports (default)
- Top 1000 scan: `--top1000`
- Full scan: all ports 1-65535 with `--full`
- Custom ports: `--ports 80,443,8000-8100`
- Service detection: shows what service is on each open port (SSH, HTTP, MySQL, RDP, and more)
- Banner grabbing: reads the service banner where available
- Live progress: open ports print immediately, with a progress line
- Save report: `--output report.txt` or `--output report.json`

## Requirements

- Python 3.8+
- No external libraries. Standard library only.

## Usage

```bash
python3 netcrash.py --help
python3 netcrash.py 192.168.1.1
python3 netcrash.py example.com --full
python3 netcrash.py 192.168.1.1 --ports 80,443,8000-8100
python3 netcrash.py example.com --top1000 --output report.json
python3 netcrash.py 192.168.1.1 --threads 200 --timeout 1.0
```

For full usage, run:

```bash
python3 netcrash.py --help
```

## Options

| Option | What it does |
|---|---|
| `target` | IP address or domain name to scan |
| `--fast` | Top 100 common ports (default) |
| `--top1000` | Top 1000 common ports |
| `--full` | All ports 1-65535 |
| `--ports 80,443,8000-8100` | Custom port list or range |
| `--threads N` | Threads, default 100, max 500 |
| `--timeout SECONDS` | Connection timeout, default 0.5 |
| `--output FILE` | Save report as .txt or .json |
| `--no-banner` | Skip banner grabbing |
| `--no-color` | Disable red coloured output |
| `--version` | Show version |

## Legal notice

Only scan systems you own or have explicit permission to test. Unauthorized scanning is illegal in many countries. The author is not responsible for misuse.
