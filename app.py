import os
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.utils.logger import get_logger
from backend.config.settings import Settings
from backend.memory.memory_store import MemoryStore
from backend.models.loader import ModelManager
from fastapi.responses import StreamingResponse, JSONResponse
import aiofiles
import json

logger = get_logger('app')

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

settings = Settings()
# attempt to load secret from env so automated packaged apps can supply passphrase via ORIUN_PASSPHRASE
env_pass = os.environ.get('ORIUN_PASSPHRASE')
try:
    secret = settings.load_secret(env_pass)
    if secret:
        settings.openai_api_key = secret
except Exception:
    secret = None

mem = MemoryStore(settings.db_path)
models = ModelManager(settings)


class ChatRequest(BaseModel):
    message: str
    tools: list = []


class PassphraseRequest(BaseModel):
    passphrase: str


@app.on_event('startup')
async def startup_event():
    logger.info('Starting Oriun backend...')
    await mem.initialize()
    # background tasks
    asyncio.create_task(mem.background_consolidate())


@app.get('/status')
async def status():
    return {'online': settings.openai_api_key is not None, 'offline_model': models.loaded_path}


@app.post('/chat')
async def chat(req: ChatRequest):
    # Very simple flow: retrieve context, call model, store memory
    ctx = mem.retrieve_context(req.message, k=5)
    # auto-select model
    resp = models.generate(req.message, context=ctx)
    # store
    mem.save_conversation('local_user', [{'role':'user','text':req.message},{'role':'assistant','text':resp}])
    return resp


@app.post('/chat/stream')
async def chat_stream(req: ChatRequest):
    # streaming response: generator yields text chunks
    async def gen():
        try:
            for chunk in models.generate_stream(req.message, context=mem.retrieve_context(req.message, k=5)):
                # ensure bytes
                if isinstance(chunk, str):
                    yield chunk.encode('utf-8')
                else:
                    yield chunk
        except Exception as e:
            yield (f"[ERROR] {e}").encode('utf-8')

    return StreamingResponse(gen(), media_type='text/event-stream')


@app.get('/memory/search')
async def memory_search(query: str = '', limit: int = 10):
    items = mem.search(query, limit=int(limit))
    return {'items': items}


@app.post('/memory/save')
async def memory_save(item: dict):
    mem.save_memory(item)
    return {'ok': True}


@app.post('/tools/image/upload')
async def upload_image(file: UploadFile = File(...)):
    out_dir = os.path.join(settings.data_dir, 'uploads')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, file.filename)
    async with aiofiles.open(path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    return {'name': file.filename, 'path': path}


@app.post('/config')
async def save_config(cfg: dict):
    settings.update(cfg)
    return {'ok': True}


@app.get('/config/permissions')
async def get_permissions():
    return settings.permissions


@app.post('/config/permissions')
async def set_permissions(p: dict):
    settings.permissions.update(p)
    settings.save()
    return settings.permissions


@app.get('/config/secret_exists')
async def secret_exists():
    return {'exists': os.path.exists(settings.secret_file)}


@app.post('/config/load_secret')
async def load_secret(req: PassphraseRequest):
    try:
        secret = settings.load_secret(req.passphrase)
        if not secret:
            return JSONResponse({'ok': False, 'error': 'Wrong passphrase or no secret found'}, status_code=400)
        settings.openai_api_key = secret
        return {'ok': True}
    except Exception as e:
        return JSONResponse({'ok': False, 'error': str(e)}, status_code=500)


@app.post('/models/load')
async def models_load(path: str):
    try:
        models.load_local_model(path)
        return {'ok': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app:app', host='127.0.0.1', port=8000, reload=True)
