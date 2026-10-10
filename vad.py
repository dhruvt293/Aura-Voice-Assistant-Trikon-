import torch
import pyaudio
import numpy as np
import wave
import time

class VADRecorder:
    def __init__(self, threshold=0.5, sampling_rate=16000):
        print("Loading Silero VAD model...")
        self.model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                           model='silero_vad',
                                           force_reload=False,
                                           trust_repo=True)
        (self.get_speech_timestamps, self.save_audio, self.read_audio, self.VADIterator, self.collect_chunks) = utils
        self.sampling_rate = sampling_rate
        self.threshold = threshold
        self.p = pyaudio.PyAudio()
        print("VAD model loaded.")

    def record(self, filename="input.wav", silence_duration=1.5, update_callback=None):
        """
        Records audio from the microphone until silence is detected.
        `update_callback` can be used to update UI states (e.g. "Listening...").
        """
        stream = self.p.open(format=pyaudio.paInt16,
                             channels=1,
                             rate=self.sampling_rate,
                             input=True,
                             frames_per_buffer=512)
                             
        if update_callback:
            update_callback("Waiting for speech...")
            
        frames = []
        speech_started = False
        silence_start_time = None
        
        while True:
            try:
                data = stream.read(512, exception_on_overflow=False)
            except IOError:
                continue
                
            frames.append(data)
            
            # Convert to torch tensor for VAD
            audio_int16 = np.frombuffer(data, np.int16)
            audio_float32 = audio_int16.astype(np.float32) / 32768.0
            tensor = torch.from_numpy(audio_float32)
            
            # Check for speech
            speech_prob = self.model(tensor, self.sampling_rate).item()
            
            if speech_prob > self.threshold:
                if not speech_started:
                    speech_started = True
                    if update_callback:
                        update_callback("Listening...")
                silence_start_time = None
            elif speech_started:
                if silence_start_time is None:
                    silence_start_time = time.time()
                elif time.time() - silence_start_time > silence_duration:
                    # Silence exceeded the duration, stop recording
                    break
                    
        stream.stop_stream()
        stream.close()
        
        if update_callback:
            update_callback("Processing...")
            
        # Save to file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sampling_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return filename
