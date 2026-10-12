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
        
    def transcribe(self, audio_file, language_hint="auto"):
        """
        Transcribes the given audio file with minimal latency.
        Restricts language strictly to English or Hindi to eliminate foreign language hallucinations (e.g. Urdu/Russian).
        Returns (text, language, latency_seconds).
        """
        import time
        if not os.path.exists(audio_file):
            return "", "en", 0.0
            
        t_start = time.time()
        
        # Determine language target
        if language_hint in ["en", "english"]:
            target_lang = "en"
        elif language_hint in ["hi", "hindi"]:
            target_lang = "hi"
        else:
            # Auto-detect between English and Hindi ONLY
            try:
                # Load audio features for fast language detection
                lang_code, lang_prob, all_probs = self.model.detect_language(audio_file)
                prob_dict = dict(all_probs) if all_probs else {}
                hi_prob = prob_dict.get("hi", 0.0)
                # If Hindi probability is high, use Hindi, otherwise strictly default to English
                if hi_prob > 0.35 or lang_code == "hi":
                    target_lang = "hi"
                else:
                    target_lang = "en"
            except Exception as e:
                print(f"Language detection fallback to en: {e}")
                target_lang = "en"

        segments, info = self.model.transcribe(
            audio_file, 
            language=target_lang,
            beam_size=1, 
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=400),
            without_timestamps=True,
            condition_on_previous_text=False,
            temperature=0.0
        )
        
        text = " ".join([segment.text for segment in segments]).strip()
        latency = round(time.time() - t_start, 3)
        
        return text, target_lang, latency
