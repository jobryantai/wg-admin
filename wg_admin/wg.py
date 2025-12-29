import subprocess

WG_INTERFACE = "wg0"


def run_cmd(cmd):
    cmd = f"sudo -n {cmd}"
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=5  # prevents hanging forever
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def wg_show():
    cmd = f"wg show {WG_INTERFACE} dump"
    out, err, code = run_cmd(cmd)
    return out if code == 0 else f"Error: {err}"


def wg_add_peer(public_key, allowed_ips):
    cmd = f"wg set {WG_INTERFACE} peer {public_key} allowed-ips {allowed_ips}"
    return run_cmd(cmd)


def wg_remove_peer(public_key):
    cmd = f"wg set {WG_INTERFACE} peer {public_key} remove"
    return run_cmd(cmd)


def wg_dump():
    """Return a list of peers from wg0 using `wg show wg0 dump`."""
    out, err, code = run_cmd(f"wg show {WG_INTERFACE} dump")
    if code != 0:
        return None

    lines = out.splitlines()
    if len(lines) < 2:
        return []

    peers = []
    for line in lines[1:]:
        parts = line.split("\t")
        if len(parts) >= 1:
            peers.append(parts[0])  # public key
    return peers

