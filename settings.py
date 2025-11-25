import os
import json
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import secrets


class Settings:
    """
    Settings with passphrase-derived secret storage.

    For production, the UI should prompt the user for a passphrase. The passphrase is
    used to derive a symmetric key (PBKDF2-HMAC-SHA256) and we store salt + encrypted token.
    The secret file layout is: base64(salt)::base64(token)
    """

    def __init__(self, path=None):
        base = os.path.dirname(__file__)
        self.path = path or os.path.join(base, 'default_settings.json')
        with open(self.path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.db_path = data.get('db_path', './data/oriun_memory.db')
        self.data_dir = data.get('data_dir', './data')
        self.openai_api_key = data.get('openai_api_key')
        self.offline_model = data.get('offline_model')
        self.permissions = data.get('permissions', {'drive': False, 'screen': False, 'automation': False})
        self.secret_file = os.path.join(self.data_dir, 'secret.enc')
        os.makedirs(self.data_dir, exist_ok=True)

    def update(self, cfg: dict, passphrase: str = None):
        # update basic keys
        if 'openai_api_key' in cfg:
            self.openai_api_key = None
            if cfg.get('openai_api_key'):
                if not passphrase:
                    raise ValueError('passphrase required to store secrets')
                self.store_secret(cfg['openai_api_key'], passphrase)
        if 'offline_model' in cfg:
            self.offline_model = cfg['offline_model']
        if 'voice' in cfg:
            self.voice = cfg['voice']
        if 'permissions' in cfg:
            self.permissions = cfg['permissions']
        # persist settings (without secret)
        self.save()

    def save(self):
        data = {'db_path': self.db_path, 'data_dir': self.data_dir, 'openai_api_key': None, 'offline_model': self.offline_model, 'permissions': self.permissions}
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _derive_key(self, passphrase: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390000, backend=default_backend())
        return base64.urlsafe_b64encode(kdf.derive(passphrase.encode('utf-8')))

    def store_secret(self, secret_value: str, passphrase: str):
        salt = secrets.token_bytes(16)
        key = self._derive_key(passphrase, salt)
        f = Fernet(key)
        token = f.encrypt(secret_value.encode('utf-8'))
        with open(self.secret_file, 'wb') as sf:
            sf.write(base64.b64encode(salt) + b'::' + base64.b64encode(token))

    def load_secret(self, passphrase: str = None):
        if not os.path.exists(self.secret_file):
            return None
        raw = open(self.secret_file, 'rb').read()
        try:
            salt_b64, token_b64 = raw.split(b'::', 1)
            salt = base64.b64decode(salt_b64)
            token = base64.b64decode(token_b64)
            if passphrase is None:
                # try environment passphrase
                passphrase = os.environ.get('ORIUN_PASSPHRASE')
                if passphrase is None:
                    raise ValueError('Passphrase required to decrypt secret')
            key = self._derive_key(passphrase, salt)
            f = Fernet(key)
            return f.decrypt(token).decode('utf-8')
        except Exception:
            return None
