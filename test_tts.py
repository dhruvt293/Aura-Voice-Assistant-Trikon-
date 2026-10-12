import traceback
from tts import TextToSpeech

try:
    tts = TextToSpeech()
    print('TTS loaded')
    tts.speak('Hello world', language='en')
    print('English ok')
    tts.speak('नमस्ते', language='hi')
    print('Hindi ok')
except Exception as e:
    traceback.print_exc()
