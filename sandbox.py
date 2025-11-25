import subprocess
import shlex
from backend.utils.logger import get_logger

logger = get_logger('sandbox')

def run_command_safe(cmd, confirm=False):
    # Only allow when user confirmed via UI and automation permission
    if not confirm:
        raise PermissionError('Command requires explicit confirmation')
    # Very simple execution wrapper
    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    return {'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}
