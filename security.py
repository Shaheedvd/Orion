import os

def check_permission(settings, action):
    # action can be: 'drive','screen','automation'
    return settings.permissions.get(action, False)


def sanitize_path(base_dir, path):
    # prevent path traversal outside the data_dir unless user explicitly allowed
    ab = os.path.abspath(path)
    if ab.startswith(os.path.abspath(base_dir)):
        return ab
    raise PermissionError('Access to path denied by sandbox')
