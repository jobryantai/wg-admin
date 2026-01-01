import subprocess

def wg_show():
    try:
        output = subprocess.check_output(["sudo", "wg", "show"], text=True)
        return output
    except:
        return "wg show failed"


def wg_add_peer(public_key, allowed_ips):
    try:
        subprocess.check_output([
            "sudo", "wg", "set", "wg0",
            "peer", public_key,
            "allowed-ips", allowed_ips
        ])
    except:
        pass


def wg_remove_peer(public_key):
    try:
        subprocess.check_output([
            "sudo", "wg", "set", "wg0",
            "peer", public_key,
            "remove"
        ])
    except:
        pass
