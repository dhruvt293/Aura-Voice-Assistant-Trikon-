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
        Transcribes the given audio file and returns the text and detected language.
        """
        if not os.path.exists(audio_file):
            return "", "en"
            
        segments, info = self.model.transcribe(audio_file, beam_size=5)
        
        text = ""
        for segment in segments:
            text += segment.text + " "
            
        return text.strip(), info.language
