import gradio as gr
from stt import SpeechToText
from llm import LanguageModel
from tts import TextToSpeech
import os

print("Initializing models (this may take a moment)...")
stt_model = SpeechToText()
llm_model = LanguageModel()
tts_model = TextToSpeech()
print("Models loaded successfully.")

def process_audio(audio_filepath):
    if not audio_filepath:
        return "No audio detected.", None
        
    try:
        # 1. Transcribe Audio
        user_text, language = stt_model.transcribe(audio_filepath)
        if not user_text.strip():
            return "Could not understand audio.", None
            
        # 2. Get LLM Response
        response_text = llm_model.chat(user_text)
        
        # 3. Generate Speech using the detected language
        output_audio_path = "output.wav"
        tts_model.speak(response_text, language=language, output_file=output_audio_path)
        
        # Format the chat history for display
        chat_log = f"**You ({language}):** {user_text}\n\n**Aura:** {response_text}"
        
        return chat_log, output_audio_path
        
    except Exception as e:
        return f"Error: {str(e)}", None

# Build the Gradio Web Interface
with gr.Blocks(title="Aura Voice AI") as demo:
    gr.Markdown("# 🎙️ Aura: Open-Weight Voice AI")
    gr.Markdown("Record your voice to chat with the AI. It uses Faster-Whisper, Llama 3.2, and Piper TTS.")
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Record your message")
            submit_btn = gr.Button("Send to Aura", variant="primary")
            
        with gr.Column():
            chat_output = gr.Markdown("Chat history will appear here...")
            audio_output = gr.Audio(label="Aura's Voice Response", autoplay=True)
            
    submit_btn.click(
        fn=process_audio,
        inputs=audio_input,
        outputs=[chat_output, audio_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, inbrowser=True)
