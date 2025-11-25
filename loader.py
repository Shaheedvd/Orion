import os
from backend.utils.logger import get_logger
from typing import Optional

logger = get_logger('models')

class ModelManager:
    def __init__(self, settings):
        self.settings = settings
        self.loaded_path: Optional[str] = None
        # detect optional libs
        try:
            import requests
            self._have_requests = True
        except Exception:
            self._have_requests = False
        try:
            import pyllamacpp
            self._have_pyllamacpp = True
        except Exception:
            self._have_pyllamacpp = False

    def load_local_model(self, path: str):
        # Placeholder to integrate with pyllamacpp or llama.cpp
        if not os.path.exists(path):
            raise FileNotFoundError('Model file not found: '+path)
        self.loaded_path = path
        logger.info('Local model registered: %s', path)

    def unload_model(self):
        self.loaded_path = None

    def generate(self, prompt: str, context: str = '') -> str:
        # Decide whether to use online OpenAI or offline model
        if self.settings.openai_api_key:
            try:
                return self._call_openai(prompt, context)
            except Exception as e:
                logger.warning('OpenAI failed, falling back to local: %s', e)
        # offline fallback
        return self._call_local_stub(prompt, context)

    def _call_openai(self, prompt: str, context: str) -> str:
        # Lightweight wrapper; user must add real implementation and keep key secure
        api_key = self.settings.load_secret() or self.settings.openai_api_key
        if not api_key:
            raise RuntimeError('No OpenAI API key available')
        if not self._have_requests:
            raise RuntimeError('requests library not available')
        import requests
        headers = {'Authorization': f'Bearer {api_key}'}
        data = {"model":"gpt-3.5-turbo","messages":[{"role":"system","content":context},{"role":"user","content":prompt}], "stream": False}
        r = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data, timeout=30)
        r.raise_for_status()
        j = r.json()
        return j['choices'][0]['message']['content']

    def _call_local_stub(self, prompt: str, context: str) -> str:
        # A deterministic very small local model stub for dev/testing
        reply = f"[LocalStub] Received: {prompt}\nContext:\n{context[:100]}"
        return reply

    def generate_stream(self, prompt: str, context: str = ''):
        # Prefer OpenAI streaming if API key is available and requests is present
        api_key = None
        try:
            api_key = self.settings.load_secret() or self.settings.openai_api_key
        except Exception:
            api_key = None

        if api_key and self._have_requests:
            # stream from OpenAI using the streaming API
            import requests
            headers = {'Authorization': f'Bearer {api_key}'}
            data = {"model":"gpt-3.5-turbo","messages":[{"role":"system","content":context},{"role":"user","content":prompt}], "stream": True}
            with requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data, stream=True, timeout=60) as r:
                r.raise_for_status()
                for line in r.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    # OpenAI streaming sends lines starting with 'data: '
                    l = line.lstrip('data: ').strip()
                    if l == '[DONE]':
                        break
                    try:
                        j = json.loads(l)
                        delta = j['choices'][0]['delta'].get('content','')
                        if delta:
                            yield delta
                    except Exception:
                        yield l
            return

        # Next, try local pyllamacpp streaming if available and model loaded
        if self._have_pyllamacpp and self.loaded_path:
            try:
                import pyllamacpp
                # Example pattern (may vary by pyllamacpp version): instantiate model once if desired
                try:
                    model = pyllamacpp.Llama(model_path=self.loaded_path)
                except Exception:
                    model = pyllamacpp.Llama(model=self.loaded_path)

                # pyllamacpp does not expose a universal streaming API in all versions; use generate with callback if available
                if hasattr(model, 'generate'):
                    # `generate` might accept a callback for tokens
                    def token_cb(token):
                        # token may be bytes or str
                        if isinstance(token, bytes):
                            token = token.decode('utf-8', errors='ignore')
                        yield token
                    # fallback: call and yield the full response
                    text = model.generate(prompt)
                    for i in range(0, len(text), 80):
                        yield text[i:i+80]
                    return
                else:
                    # fallback apply
                    text = model.apply(prompt)
                    for i in range(0, len(text), 80):
                        yield text[i:i+80]
                    return
            except Exception as e:
                logger.warning('pyllamacpp streaming error: %s', e)

        # fallback to local stub chunking
        text = self._call_local_stub(prompt, context)
        for i in range(0, len(text), 80):
            yield text[i:i+80]
        return
