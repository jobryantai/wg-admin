import subprocess

def wg_show():
    try:
        return subprocess.check_output(["sudo", "wg", "show"], text=True)
    except:
        return "wg show failed"

# These are no longer needed once sync_full_config() is used everywhere
def wg_add_peer(public_key, allowed_ips):
    pass

def wg_remove_peer(public_key):
    pass
