import json
from backend.memory.memory_store import MemoryStore

def export_to_json(db_path, out_path):
    ms = MemoryStore(db_path)
    # naive export: dump memory_nodes and conversations
    import sqlite3
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT id, title, summary, metadata FROM memory_nodes')
    nodes = [{'id': r[0], 'title': r[1], 'summary': r[2], 'metadata': r[3]} for r in c.fetchall()]
    c.execute('SELECT id, user_id, role, text, timestamp FROM conversations')
    conv = [{'id': r[0], 'user_id': r[1], 'role': r[2], 'text': r[3], 'timestamp': r[4]} for r in c.fetchall()]
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'nodes': nodes, 'conversations': conv}, f, indent=2)
    return out_path
