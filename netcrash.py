#!/usr/bin/env python3
"""
NetCrash V1.0 - Fast Port Scanner
Hack The Planet - hackthepalnte.co.uk

A fast, threaded TCP port scanner for authorized testing only.
Scan only systems you own or have explicit permission to test.

Usage:
    netcrash example.com
    netcrash <target> --full
    netcrash <target> --ports 80,443,8000-8100
    netcrash --help

Install it once so the short command works (see install.sh):
    sudo cp netcrash.py /usr/local/bin/netcrash

No external dependencies. Python 3.8+ only.
"""

import argparse
import concurrent.futures
import json
import socket
import sys
import threading
import time
from datetime import datetime

VERSION = "1.0"
TOOL_NAME = "NetCrash"

# ---------------------------------------------------------------------------
# Colours - full red theme
# ---------------------------------------------------------------------------

RED = "\033[91m"
RED_BOLD = "\033[1;91m"
RED_DIM = "\033[31m"
RESET = "\033[0m"
BOLD = "\033[1m"

USE_COLOR = True


def red(text, bold=False):
    if not USE_COLOR:
        return text
    return (RED_BOLD if bold else RED) + text + RESET


def dim_red(text):
    if not USE_COLOR:
        return text
    return RED_DIM + text + RESET


# ---------------------------------------------------------------------------
# Banner - block style, full red
# ---------------------------------------------------------------------------

BANNER = r"""
 ███╗   ██╗███████╗████████╗ ██████╗██████╗  █████╗ ███████╗██╗  ██╗
 ████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║
 ██╔██╗ ██║█████╗     ██║   ██║     ██████╔╝███████║███████╗███████║
 ██║╚██╗██║██╔══╝     ██║   ██║     ██╔══██╗██╔══██║╚════██║██╔══██║
 ██║ ╚████║███████╗   ██║   ╚██████╗██║  ██║██║  ██║███████║██║  ██║
 ╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
"""


def print_banner():
    print(red(BANNER, bold=True))
    print(red("                    NetCrash V1.0", bold=True))
    print(dim_red("              Hack The Planet - hackthepalnte.co.uk"))
    print()


def print_warning():
    print("Only scan systems you own or have permission to test.")
    print()


def print_short_usage():
    print("Usage: netcrash example.com")
    print("For all options: netcrash --help")


# ---------------------------------------------------------------------------
# Port lists
# ---------------------------------------------------------------------------

TOP_100 = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995,
    1723, 3306, 3389, 5432, 5900, 8080, 8443, 20, 88, 113, 119, 161,
    179, 389, 427, 465, 513, 514, 515, 548, 554, 563, 587, 636, 873,
    902, 989, 990, 1025, 1080, 1194, 1433, 1521, 1720, 1883, 2049,
    2082, 2083, 2086, 2087, 2095, 2096, 2181, 2222, 2375, 2376, 2483,
    2484, 3128, 3260, 3690, 4369, 5000, 5631, 5985, 5986, 6379, 7001,
    8000, 8008, 8009, 8081, 8088, 8888, 9000, 9042, 9090, 9200, 9300,
    10000, 7, 13, 37, 79, 106, 199, 256, 6666, 6667,
    8001, 8082, 8090, 8444, 9100, 9999,
]

HIGH_COMMON = [
    1433, 1521, 1723, 1883, 2049, 2082, 2083, 2086, 2087, 2095, 2096,
    2181, 2222, 2375, 2376, 3128, 3306, 3389, 3690, 4369, 5000, 5432,
    5900, 5985, 5986, 6379, 7001, 8000, 8008, 8009, 8080, 8081, 8088,
    8443, 8888, 9000, 9042, 9090, 9200, 9300, 10000, 27017,
]

# Top 1000: priority order (TOP_100, then high common ports, then 1-1024,
# then 1025+) sliced to exactly 1000, then sorted for scanning.
_PRIORITY_1000 = TOP_100 + HIGH_COMMON + list(range(1, 1025)) + list(range(1025, 5000))
TOP_1000 = sorted(list(dict.fromkeys(_PRIORITY_1000))[:1000])

# Common service names
SERVICES = {
    20: "FTP-Data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 67: "DHCP", 68: "DHCP", 69: "TFTP", 80: "HTTP",
    110: "POP3", 111: "RPC", 123: "NTP", 135: "MS-RPC", 137: "NetBIOS",
    138: "NetBIOS", 139: "NetBIOS", 143: "IMAP", 161: "SNMP",
    162: "SNMP-Trap", 179: "BGP", 389: "LDAP", 443: "HTTPS",
    445: "SMB", 465: "SMTPS", 514: "Syslog", 515: "Printer",
    548: "AFP", 554: "RTSP", 587: "SMTP", 631: "IPP", 636: "LDAPS",
    873: "rsync", 989: "FTPS", 990: "FTPS", 993: "IMAPS",
    995: "POP3S", 1025: "NFS", 1080: "SOCKS", 1194: "OpenVPN",
    1433: "MSSQL", 1521: "Oracle", 1723: "PPTP", 1883: "MQTT",
    2049: "NFS", 2082: "cPanel", 2083: "cPanel-SSL", 2086: "WHM",
    2087: "WHM-SSL", 2095: "cPanel-Webmail", 2096: "cPanel-Webmail-SSL",
    2181: "Zookeeper", 2222: "SSH-Alt", 2375: "Docker", 2376: "Docker-SSL",
    2483: "Oracle-SSL", 2484: "Oracle-SSL", 3128: "Proxy",
    3260: "iSCSI", 3306: "MySQL", 3389: "RDP", 3690: "SVN",
    4369: "Erlang", 5000: "Flask / UPnP", 5432: "PostgreSQL",
    5631: "PCAnywhere", 5900: "VNC", 5985: "WinRM", 5986: "WinRM-SSL",
    6379: "Redis", 7001: "Cassandra", 8000: "HTTP-Alt", 8008: "HTTP-Alt",
    8009: "AJP", 8080: "HTTP-Proxy", 8081: "HTTP-Alt", 8088: "HTTP-Alt",
    8443: "HTTPS-Alt", 8834: "Nessus", 8888: "HTTP-Alt", 9000: "Sonar / PHP-FPM",
    9042: "Cassandra", 9090: "Webmin", 9100: "Printer", 9200: "Elasticsearch",
    9300: "Elasticsearch", 10000: "Webmin", 27017: "MongoDB",
}


def service_name(port):
    if port in SERVICES:
        return SERVICES[port]
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"


# ---------------------------------------------------------------------------
# Port parsing
# ---------------------------------------------------------------------------

def parse_ports(spec):
    """Parse '80,443,8000-8100' into a sorted list of ports."""
    ports = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            try:
                start, end = part.split("-", 1)
                start, end = int(start), int(end)
            except ValueError:
                raise ValueError(f"Invalid port range: {part}")
            if not (1 <= start <= 65535 and 1 <= end <= 65535):
                raise ValueError(f"Port out of range: {part}")
            if start > end:
                start, end = end, start
            ports.update(range(start, end + 1))
        else:
            try:
                port = int(part)
            except ValueError:
                raise ValueError(f"Invalid port: {part}")
            if not 1 <= port <= 65535:
                raise ValueError(f"Port out of range: {port}")
            ports.add(port)
    return sorted(ports)


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------

def grab_banner(sock, port, timeout):
    """Try to read a service banner. Returns a short clean string or ''."""
    try:
        sock.settimeout(timeout)
        # HTTP-like ports: send a HEAD request to get a response
        if port in (80, 8080, 8000, 8008, 8009, 8081, 8088, 8888, 9000):
            try:
                sock.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
            except OSError:
                pass
        try:
            data = sock.recv(1024)
        except (socket.timeout, OSError):
            return ""
        if not data:
            return ""
        text = data.decode("utf-8", errors="ignore").strip()
        # Keep only the first line, clean it up
        first = text.splitlines()[0] if text.splitlines() else ""
        first = "".join(c for c in first if c.isprintable())
        return first[:80]
    except OSError:
        return ""


def scan_port(target_ip, port, timeout, grab):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target_ip, port))
        if result != 0:
            sock.close()
            return None
        banner = ""
        if grab:
            banner = grab_banner(sock, port, timeout)
        sock.close()
        return {
            "port": port,
            "service": service_name(port),
            "banner": banner,
        }
    except OSError:
        return None


# ---------------------------------------------------------------------------
# Save results
# ---------------------------------------------------------------------------

def save_results(path, target, target_ip, results, elapsed, mode):
    is_json = path.lower().endswith(".json")
    data = {
        "tool": f"{TOOL_NAME} V{VERSION}",
        "target": target,
        "ip": target_ip,
        "mode": mode,
        "scanned_at": datetime.now().isoformat(timespec="seconds"),
        "scan_time_seconds": round(elapsed, 2),
        "open_ports": len(results),
        "results": results,
    }
    try:
        with open(path, "w", encoding="utf-8") as f:
            if is_json:
                json.dump(data, f, indent=2)
            else:
                f.write(f"{TOOL_NAME} V{VERSION} - Scan Report\n")
                f.write(f"Target: {target} ({target_ip})\n")
                f.write(f"Mode: {mode}\n")
                f.write(f"Date: {data['scanned_at']}\n")
                f.write(f"Scan time: {data['scan_time_seconds']}s\n")
                f.write(f"Open ports: {len(results)}\n")
                f.write("-" * 60 + "\n")
                f.write(f"{'PORT':<8}{'SERVICE':<20}{'BANNER'}\n")
                f.write("-" * 60 + "\n")
                for r in results:
                    f.write(f"{r['port']:<8}{r['service']:<20}{r['banner']}\n")
        return True
    except OSError as e:
        print(f"Error: Could not save report to {path}: {e}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="netcrash",
        description="NetCrash V1.0 - Fast threaded TCP port scanner. "
                    "Scan only systems you own or have permission to test.",
        epilog="Examples:\n"
               "  netcrash 192.168.1.1\n"
               "  netcrash example.com --full\n"
               "  netcrash 192.168.1.1 --ports 80,443,8000-8100\n"
               "  netcrash example.com --top1000 --output report.json\n"
               "  netcrash 192.168.1.1 --threads 200 --timeout 1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("target", nargs="?", help="Target IP address or domain name")
    parser.add_argument("--fast", action="store_true",
                        help="Scan top 100 common ports (default)")
    parser.add_argument("--top1000", action="store_true",
                        help="Scan top 1000 common ports")
    parser.add_argument("--full", action="store_true",
                        help="Scan all ports 1-65535")
    parser.add_argument("--ports", metavar="PORTS",
                        help="Custom ports, e.g. 80,443,8000-8100")
    parser.add_argument("--threads", type=int, default=100, metavar="N",
                        help="Number of threads (default: 100, max: 500)")
    parser.add_argument("--timeout", type=float, default=0.5, metavar="SECONDS",
                        help="Connection timeout in seconds (default: 0.5)")
    parser.add_argument("--output", metavar="FILE",
                        help="Save report to file (.txt or .json)")
    parser.add_argument("--no-banner", action="store_true",
                        help="Do not grab service banners")
    parser.add_argument("--no-color", action="store_true",
                        help="Disable coloured output")
    parser.add_argument("--version", action="version",
                        version=f"NetCrash V{VERSION}")
    return parser


def resolve_target(target):
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        return None


def main(argv=None):
    global USE_COLOR
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.no_color:
        USE_COLOR = False
    elif not sys.stdout.isatty():
        USE_COLOR = False

    if not args.target:
        print_banner()
        print_short_usage()
        return 2

    # Choose port set - one mode only
    modes = [args.fast, args.top1000, args.full, bool(args.ports)]
    if sum(modes) > 1:
        parser.error("Use only one of --fast, --top1000, --full or --ports.")

    if args.ports:
        try:
            ports = parse_ports(args.ports)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 2
        mode_name = f"custom ({args.ports})"
    elif args.full:
        ports = list(range(1, 65536))
        mode_name = "full (1-65535)"
    elif args.top1000:
        ports = TOP_1000
        mode_name = "top 1000"
    else:
        ports = TOP_100
        mode_name = "fast (top 100)"

    if not 1 <= args.threads <= 500:
        print("Error: --threads must be between 1 and 500.", file=sys.stderr)
        return 2
    if args.timeout <= 0 or args.timeout > 10:
        print("Error: --timeout must be between 0 and 10 seconds.", file=sys.stderr)
        return 2

    print_banner()
    print_warning()

    target_ip = resolve_target(args.target)
    if not target_ip:
        print(f"Error: Could not resolve '{args.target}'. Check the address and try again.",
              file=sys.stderr)
        return 2

    print(f"Target: {args.target} ({target_ip})")
    print(f"Mode: {mode_name}  |  Ports: {len(ports)}  |  Threads: {args.threads}")
    print()

    results = []
    scanned = 0
    total = len(ports)
    lock = threading.Lock()
    stop_progress = False

    last_progress = [0.0]

    def show_progress(force=False):
        now = time.time()
        if not force and now - last_progress[0] < 0.25:
            return
        last_progress[0] = now
        with lock:
            percent = (scanned / total * 100) if total else 100
            sys.stdout.write(
                f"\rScanning... {scanned}/{total} ports ({percent:.0f}%)  "
                f"Open: {len(results)}"
            )
            sys.stdout.flush()

    start = time.time()

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as pool:
            futures = {
                pool.submit(scan_port, target_ip, port, args.timeout, not args.no_banner): port
                for port in ports
            }
            for future in concurrent.futures.as_completed(futures):
                port = futures[future]
                try:
                    found = future.result()
                except Exception:
                    found = None
                with lock:
                    scanned += 1
                    if found:
                        results.append(found)
                # Open port: print immediately, on its own line
                if found:
                    sys.stdout.write("\r" + " " * 70 + "\r")
                    banner_text = f"  {found['banner']}" if found["banner"] else ""
                    print(f"[+] {found['port']:<6} open  {found['service']}{banner_text}")
                show_progress()
    except KeyboardInterrupt:
        print("\n\nScan stopped by user.")
        elapsed = time.time() - start
        results.sort(key=lambda r: r["port"])
        print(f"\nPartial results: {len(results)} open port(s) found in {elapsed:.2f}s.")
        if args.output and results:
            save_results(args.output, args.target, target_ip, results, elapsed, mode_name)
            print(f"Report saved to {args.output}")
        return 130

    elapsed = time.time() - start
    show_progress(force=True)
    sys.stdout.write("\r" + " " * 70 + "\r")
    print()
    results.sort(key=lambda r: r["port"])

    print(f"{'PORT':<8}{'SERVICE':<20}{'BANNER'}")
    print("-" * 60)
    if results:
        for r in results:
            print(f"{r['port']:<8}{r['service']:<20}{r['banner']}")
    else:
        print("No open ports found.")
    print("-" * 60)
    print(f"Done. {len(results)} open port(s) out of {total} scanned in {elapsed:.2f}s.")

    if args.output:
        if save_results(args.output, args.target, target_ip, results, elapsed, mode_name):
            print(f"Report saved to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
