import os
from backend.utils.security import check_permission, sanitize_path

def list_dir(settings, path='.'):
    if not check_permission(settings, 'drive'):
        raise PermissionError('Drive permission not granted')
    base = settings.data_dir
    p = sanitize_path(base, path)
    items = []
    for name in os.listdir(p):
        items.append(name)
    return items

def read_file(settings, path):
    if not check_permission(settings, 'drive'):
        raise PermissionError('Drive permission not granted')
    p = sanitize_path(settings.data_dir, path)
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def write_file(settings, path, content, dry=False):
    if not check_permission(settings, 'drive'):
        raise PermissionError('Drive permission not granted')
    p = sanitize_path(settings.data_dir, path)
    if dry:
        return {'path': p, 'ok': True, 'dry': True}
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)
    return {'path': p, 'ok': True}
