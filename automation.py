import os, shutil
from backend.utils.logger import get_logger

logger = get_logger('automation')

def organize_by_extension(settings, folder, dry=True):
    if not settings.permissions.get('drive'):
        raise PermissionError('Drive permission required')
    folder = os.path.abspath(folder)
    ops = []
    for fname in os.listdir(folder):
        full = os.path.join(folder, fname)
        if os.path.isfile(full):
            ext = os.path.splitext(fname)[1].lstrip('.') or 'noext'
            destdir = os.path.join(folder, ext)
            dest = os.path.join(destdir, fname)
            ops.append({'src': full, 'dest': dest})
    if dry:
        return {'dry': True, 'ops': ops}
    # apply
    for op in ops:
        os.makedirs(os.path.dirname(op['dest']), exist_ok=True)
        shutil.move(op['src'], op['dest'])
    return {'ok': True, 'moved': len(ops)}
