import subprocess
import time
import requests
import os


def start_backend(port=8900):
    # run uvicorn in a subprocess
    cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    p = subprocess.Popen(['python', '-m', 'uvicorn', 'app:app', '--port', str(port)], cwd=cwd)
    # wait for startup
    for _ in range(10):
        try:
            r = requests.get(f'http://127.0.0.1:{port}/status', timeout=1)
            if r.status_code == 200:
                return p
        except Exception:
            time.sleep(0.5)
    return p


def stop_backend(p):
    p.terminate()
    try:
        p.wait(timeout=5)
    except Exception:
        p.kill()


def test_stream_flow():
    port = 8900
    p = start_backend(port=port)
    try:
        r = requests.post(f'http://127.0.0.1:{port}/chat/stream', json={'message': 'Hello', 'tools': []}, stream=True, timeout=30)
        assert r.status_code == 200
        chunks = []
        for chunk in r.iter_content(chunk_size=64):
            if chunk:
                chunks.append(chunk.decode('utf-8'))
        text = ''.join(chunks)
        assert 'LocalStub' in text or len(text) > 0
    finally:
        stop_backend(p)

