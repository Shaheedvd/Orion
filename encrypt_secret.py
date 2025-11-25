#!/usr/bin/env python3
"""
Encrypt a secret (e.g., OpenAI API key) into backend/data/secret.enc using a passphrase.

Usage (PowerShell):

 $env:ORIUN_PASSPHRASE = Read-Host -AsSecureString "Enter passphrase" | ConvertFrom-SecureString
 # Or run interactively; the script will prompt for passphrase if ORIUN_PASSPHRASE is not set
 python encrypt_secret.py --secret "sk-..."

This script does NOT store your passphrase in the repository. It will store only the encrypted token and salt in `backend/data/secret.enc`.
"""
import argparse
import getpass
import os
import sys
# Try to import Settings from local package; make script runnable from backend/ dir
if __package__ is None:
    # ensure backend/ is on sys.path when running this script directly
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
try:
    from config.settings import Settings
except Exception:
    # fallback to previous import path
    from backend.config.settings import Settings

def main():
    parser = argparse.ArgumentParser(description='Encrypt a secret into backend/data/secret.enc')
    parser.add_argument('--secret', help='Secret to encrypt (if omitted, will prompt)')
    parser.add_argument('--passphrase', help='Passphrase to use (if omitted, will prompt)')
    args = parser.parse_args()

    secret = args.secret
    if not secret:
        secret = getpass.getpass('Enter secret to encrypt (will not echo): ')

    passphrase = args.passphrase
    if not passphrase:
        # Try environment variable ORIUN_PASSPHRASE first
        passphrase = os.environ.get('ORIUN_PASSPHRASE')
        if not passphrase:
            passphrase = getpass.getpass('Enter passphrase to protect secret (will not echo): ')

    s = Settings()
    s.store_secret(secret, passphrase)
    print('Secret encrypted to:', s.secret_file)

if __name__ == '__main__':
    main()
