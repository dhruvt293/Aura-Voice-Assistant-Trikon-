import os
import wave
import pyaudio
import urllib.request
from piper import PiperVoice

class TextToSpeech:
    def __init__(self):
        self.model_dir = "models"
        self.en_model = os.path.join(self.model_dir, "en_US-lessac-medium.onnx")
        self.en_json = os.path.join(self.model_dir, "en_US-lessac-medium.onnx.json")
        self.hi_model = os.path.join(self.model_dir, "hi_IN-swara-medium.onnx")
        self.hi_json = os.path.join(self.model_dir, "hi_IN-swara-medium.onnx.json")
        
        self.download_models()
        
        print("Loading Piper TTS voices (English & Hindi)...")
        self.en_voice = PiperVoice.load(self.en_model)
        self.hi_voice = PiperVoice.load(self.hi_model)
        print("Piper TTS loaded.")
        
    def download_models(self):
        os.makedirs(self.model_dir, exist_ok=True)
        # English
        if not os.path.exists(self.en_model):
            print("Downloading English voice...")
            urllib.request.urlretrieve("https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx", self.en_model)
            urllib.request.urlretrieve("https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json", self.en_json)
        # Hindi
        if not os.path.exists(self.hi_model):
            print("Downloading Hindi voice...")
            urllib.request.urlretrieve("https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/hi/hi_IN/pratham/medium/hi_IN-pratham-medium.onnx", self.hi_model)
            urllib.request.urlretrieve("https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/hi/hi_IN/pratham/medium/hi_IN-pratham-medium.onnx.json", self.hi_json)
            
    def speak(self, text, language="en", output_file="output.wav"):
        """
        Synthesizes text to speech with a constant, fluent female voice.
        Returns (output_file, latency_seconds).
        """
        import time
        t_start = time.time()
        
        # Always use the natural, fluent English female voice (Lessac)
        voice = self.en_voice
        
        # Clean text for smoother synthesis (remove quotes, asterisks, brackets)
        clean_text = text.replace("*", "").replace("#", "").replace('"', '').replace("'", "").strip()
        if not clean_text:
            clean_text = "I am listening."
        
        # Synthesize audio to a WAV file
        with wave.open(output_file, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(voice.config.sample_rate)
            # Write each chunk of audio to the wave file
            for chunk in voice.synthesize(clean_text):
                wav_file.writeframes(chunk.audio_int16_bytes)
            
        latency = round(time.time() - t_start, 3)
        return output_file, latency
        
    def play_audio(self, file_path):
        chunk = 1024
        wf = wave.open(file_path, 'rb')
        p = pyaudio.PyAudio()
        
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        
        data = wf.readframes(chunk)
        while data:
            stream.write(data)
            data = wf.readframes(chunk)
            
        stream.stop_stream()
        stream.close()
        p.terminate()
