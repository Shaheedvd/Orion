import os
import sqlite3
import json
import time
import threading
from sentence_transformers import SentenceTransformer
import numpy as np
try:
    import faiss
    HAS_FAISS = True
except Exception:
    HAS_FAISS = False

from backend.utils.logger import get_logger

logger = get_logger('memory')

class MemoryStore:
    def __init__(self, db_path='./data/oriun_memory.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._conn = None
        self.embed_model = None
        self.index = None

    async def initialize(self):
        if not os.path.exists(self.db_path):
            self._conn = sqlite3.connect(self.db_path)
            schema = open(os.path.join(os.path.dirname(__file__), 'db_schema.sql')).read()
            self._conn.executescript(schema)
            self._conn.commit()
        else:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        # load embedder
        try:
            self.embed_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.warning('Could not load sentence-transformers: %s', e)
            self.embed_model = None
        # build index
        if HAS_FAISS:
            self._ensure_faiss()

    def _ensure_faiss(self):
        # reconstruct index from DB embeddings
        c = self._conn.cursor()
        c.execute('SELECT id, vector FROM embeddings')
        rows = c.fetchall()
        if rows:
            vec = np.vstack([np.frombuffer(r[1], dtype=np.float32) for r in rows])
            dim = vec.shape[1]
            idx = faiss.IndexFlatL2(dim)
            idx.add(vec)
            self.index = idx

    def save_conversation(self, user, messages):
        c = self._conn.cursor()
        for m in messages:
            c.execute('INSERT INTO conversations (user_id, role, text) VALUES ((SELECT id FROM users WHERE name=?), ?, ?)', (user, m.get('role'), m.get('text')))
        self._conn.commit()

    def save_memory(self, item: dict):
        c = self._conn.cursor()
        title = item.get('title') or item.get('summary','')[:80]
        summary = item.get('summary','')
        metadata = json.dumps(item.get('metadata',{}))
        c.execute('INSERT INTO memory_nodes (title, summary, metadata) VALUES (?,?,?)', (title, summary, metadata))
        nid = c.lastrowid
        self._conn.commit()
        # compute embedding
        if self.embed_model:
            v = self.embed_model.encode(summary)
            vb = v.astype('float32').tobytes()
            c.execute('INSERT INTO embeddings (node_id, vector) VALUES (?,?)', (nid, vb))
            self._conn.commit()
            if HAS_FAISS:
                if self.index is None:
                    self.index = faiss.IndexFlatL2(len(v))
                self.index.add(np.array([v], dtype='float32'))

    def search(self, query: str, limit: int = 10):
        # pure keyword fallback
        c = self._conn.cursor()
        if not query or query == '_recent':
            c.execute('SELECT role, text FROM conversations ORDER BY timestamp DESC LIMIT ?', (limit,))
            return [{'role': r[0], 'text': r[1]} for r in c.fetchall()]
        if self.embed_model and HAS_FAISS and self.index is not None:
            qv = self.embed_model.encode(query).astype('float32')
            D, I = self.index.search(np.array([qv]), k=limit)
            # map indices to nodes: naive: read embeddings table order
            c.execute('SELECT node_id FROM embeddings')
            node_ids = [r[0] for r in c.fetchall()]
            results = []
            for i in I[0]:
                if i < len(node_ids):
                    nid = node_ids[i]
                    c.execute('SELECT title, summary FROM memory_nodes WHERE id=?', (nid,))
                    r = c.fetchone()
                    if r:
                        results.append({'title': r[0], 'summary': r[1]})
            return results
        else:
            c.execute('SELECT title, summary FROM memory_nodes WHERE summary LIKE ? OR title LIKE ? LIMIT ?', (f'%{query}%', f'%{query}%', limit))
            return [{'title': r[0], 'summary': r[1]} for r in c.fetchall()]

    def retrieve_context(self, query: str, k:int=5):
        items = self.search(query, limit=k)
        return '\n'.join([it.get('summary') or it.get('text','') for it in items])

    async def background_consolidate(self):
        # periodic consolidation: merge similar memory nodes (very simple)
        while True:
            try:
                logger.info('Memory consolidation tick')
                # TODO: implement proper clustering
            except Exception as e:
                logger.error('Consolidation error: %s', e)
            await asyncio.sleep(60*60)  # hourly
