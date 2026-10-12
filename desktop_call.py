import time
import os
import wave
import numpy as np
import pyaudio
import torch

from stt import SpeechToText
from llm import LanguageModel
from tts import TextToSpeech

class ContinuousVoiceCall:
    def __init__(self, sample_rate=16000, silence_limit_sec=0.75):
        self.sample_rate = sample_rate
        self.silence_limit_sec = silence_limit_sec
        self.chunk_size = 512
        
        print("\n" + "="*50)
        print("  Aura - Continuous Live Voice Call Assistant")
        print("="*50 + "\n")
        print("Loading AI pipeline...")
        self.stt = SpeechToText()
        self.llm = LanguageModel()
        self.tts = TextToSpeech()
        
        # Load Silero VAD
        print("Loading Silero Voice Activity Detector...")
        self.vad_model, _ = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            trust_repo=True
        )
        self.p = pyaudio.PyAudio()
        print("Ready for continuous conversation!\n")
        
    def listen_for_turn(self):
        """
        Continuously listens to microphone.
        Detects speech onset and automatically stops when user pauses (silence threshold).
        """
        stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        print("\n[🎙️ Live Call Active] Listening... (speak in English or Hindi)")
        frames = []
        speech_started = False
        silence_start = None
        
        while True:
            try:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
            except IOError:
                continue
                
            frames.append(data)
            
            # Convert audio chunk to torch tensor for VAD
            audio_int16 = np.frombuffer(data, np.int16)
            audio_float32 = audio_int16.astype(np.float32) / 32768.0
            tensor = torch.from_numpy(audio_float32)
            
            speech_prob = self.vad_model(tensor, self.sample_rate).item()
            
            if speech_prob > 0.45:
                if not speech_started:
                    speech_started = True
                    print("  -> Speech detected...")
                silence_start = None
            elif speech_started:
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > self.silence_limit_sec:
                    # User finished speaking!
                    print("  -> Turn complete. Processing response...")
                    break
                    
        stream.stop_stream()
        stream.close()
        
        # Save utterance
        temp_wav = "user_turn.wav"
        wf = wave.open(temp_wav, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return temp_wav
        
    def run(self):
        print("\n" + "*"*50)
        print("  CALL CONNECTED. Speak naturally. Press Ctrl+C to hang up.")
        print("*"*50)
        
        while True:
            try:
                # 1. Continuous Listen
                audio_file = self.listen_for_turn()
                
                t_total_start = time.time()
                
                # 2. Faster-Whisper STT
                user_text, lang, stt_sec = self.stt.transcribe(audio_file)
                if not user_text.strip():
                    continue
                    
                print(f"\n👤 You [{lang.upper()}]: {user_text}")
                
                # 3. Qwen-2.5 0.5B LLM
                reply_text, llm_sec = self.llm.chat(user_text, language=lang)
                print(f"🤖 Aura: {reply_text}")
                
                # 4. Piper TTS
                output_wav = "aura_reply.wav"
                _, tts_sec = self.tts.speak(reply_text, language=lang, output_file=output_wav)
                
                total_latency = round(time.time() - t_total_start, 2)
                print(f"⚡ Latency: {total_latency}s | STT: {int(stt_sec*1000)}ms | LLM: {int(llm_sec*1000)}ms | TTS: {int(tts_sec*1000)}ms")
                
                # 5. Playback
                print("🔊 Speaking back...")
                self.tts.play_audio(output_wav)
                
                # Seamlessly re-enters the loop for next turn!
                
            except KeyboardInterrupt:
                print("\n\n📞 Call ended by user. Goodbye!")
                break
            except Exception as e:
                print(f"Error in conversation loop: {e}")
                time.sleep(1)

if __name__ == "__main__":
    call = ContinuousVoiceCall()
    call.run()
