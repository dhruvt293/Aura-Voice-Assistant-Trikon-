from faster_whisper import WhisperModel
import os

class SpeechToText:
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        """
        Initializes the Faster-Whisper model for STT.
        Using 'base' model and 'cpu' by default to ensure maximum compatibility.
        """
        print(f"Loading Whisper model ({model_size})...")
        # suppress logging output from whisper if possible
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("Whisper model loaded.")
        
    def transcribe(self, audio_file):
        """
        Transcribes the given audio file with minimal latency.
        Returns (text, language, latency_seconds).
        """
        import time
        if not os.path.exists(audio_file):
            return "", "en", 0.0
            
        t_start = time.time()
        # beam_size=1 for maximum speed (greedy decoding)
        # vad_filter=True to trim non-speech audio
        segments, info = self.model.transcribe(
            audio_file, 
            beam_size=1, 
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        text = " ".join([segment.text for segment in segments]).strip()
        latency = round(time.time() - t_start, 3)
        
        lang = info.language if info.language else "en"
        return text, lang, latency
