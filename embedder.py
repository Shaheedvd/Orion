import os
from backend.utils.logger import get_logger
logger = get_logger('embedder')

class Embedder:
    def __init__(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.kind = 'local'
        except Exception as e:
            logger.warning('Local embedder not available: %s', e)
            self.model = None
            self.kind = 'none'

    def embed(self, texts):
        if self.model:
            return self.model.encode(texts)
        raise RuntimeError('No embedder available')
