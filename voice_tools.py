import pyttsx3
from backend.utils.logger import get_logger
logger = get_logger('voice')

def tts(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    return {'ok': True}

def stt_from_file(path):
    # Prefer VOSK if installed, else try Whisper if available
    try:
        from vosk import Model, KaldiRecognizer
        # TODO: streaming recognition - simplified for demo
        return {'text': '[VOSK transcription placeholder]'}
    except Exception:
        try:
            import whisper
            model = whisper.load_model('tiny')
            res = model.transcribe(path)
            return {'text': res.get('text','')}
        except Exception:
            return {'error': 'No offline STT available'}
