import tempfile
from backend.memory.memory_store import MemoryStore

def test_memory_save_and_search():
    tf = tempfile.NamedTemporaryFile(delete=False)
    ms = MemoryStore(db_path=tf.name)
    import asyncio
    asyncio.get_event_loop().run_until_complete(ms.initialize())
    ms.save_memory({'title':'t1','summary':'this is a test memory about AI'})
    results = ms.search('AI', limit=5)
    assert any('AI' in (r.get('summary') or '') for r in results)
