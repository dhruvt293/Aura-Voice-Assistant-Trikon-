from transformers import pipeline

class LanguageModel:
    def __init__(self, model_name="Qwen/Qwen2.5-0.5B-Instruct"): 
        print(f"Loading LLM ({model_name}) from Hugging Face...")
        # We use a very fast 0.5B model that runs excellently on CPU/Local setups
        self.generator = pipeline(
            "text-generation", 
            model=model_name, 
            device="cpu" # Force CPU to avoid accelerate/device_map hanging
        )
        print("LLM loaded.")
        
        self.system_prompt = {
            "role": "system", 
            "content": (
                "You are Aura, an AI voice assistant on a live phone call. "
                "Respond naturally in 1 or 2 concise, spoken sentences. "
                "Never use markdown formatting, bullet points, asterisks, or lists. "
                "Always reply in the exact same language the user spoke (Hindi or English)."
            )
        }
        self.messages = [self.system_prompt]
        
    def chat(self, user_text, language="en"):
        """
        Sends user text to the LLM and strictly responds in the user's language.
        Returns (response_text, latency_seconds).
        """
        import time
        
        # Detect if text contains Hindi characters or language was detected as Hindi
        has_devanagari = any('\u0900' <= char <= '\u097F' for char in user_text)
        is_hindi = (language in ["hi", "hindi"]) or has_devanagari
        
        if is_hindi:
            system_instruction = (
                "You are Aura, an AI voice assistant on a live phone call. "
                "The user is speaking in Hindi. You MUST respond strictly in conversational Hindi. "
                "Write your Hindi reply in Roman/Latin script (Hinglish) so it can be spoken out loud fluently. "
                "Example: 'Namaste! Main bilkul theek hoon, aap batayein?' "
                "Keep your answer to exactly 1 short spoken sentence. Never use markdown, bullet points, or English."
            )
        else:
            system_instruction = (
                "You are Aura, a friendly female AI voice assistant on a live phone call. "
                "The user is speaking in English. You MUST respond in fluent English. "
                "Keep your answer to exactly 1 concise, natural spoken sentence. "
                "Never use markdown, bullet points, asterisks, or lists."
            )
            
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_text}
        ]
            
        t_start = time.time()
        try:
            result = self.generator(
                messages, 
                max_new_tokens=32, 
                temperature=0.4,
                do_sample=True,
                pad_token_id=self.generator.tokenizer.eos_token_id
            )
            generated_messages = result[0]["generated_text"]
            reply = generated_messages[-1]["content"].strip()
            
            # Clean any stray formatting
            reply = reply.replace("*", "").replace("#", "").replace('"', '').strip()
            
            latency = round(time.time() - t_start, 3)
            return reply, latency
        except Exception as e:
            print(f"Error generating text: {e}")
            latency = round(time.time() - t_start, 3)
            if is_hindi:
                return "Namaste! Main sun rahi hoon, kripya dobara bolein.", latency
            return "I am listening. Could you please repeat that?", latency
    
    def reset_context(self):
        """
        Clears the conversation history to start fresh.
        """
        self.messages = [self.system_prompt]
