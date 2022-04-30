import subprocess
import shlex


def execute(cmd):
    """Execute a command on the target host."""
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()

res = execute('ls -l')
print(res)