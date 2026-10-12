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
        Sends user text to the LLM and returns (response_text, latency_seconds).
        """
        import time
        self.messages.append({"role": "user", "content": user_text})
        
        # Keep conversation history bounded to last 6 turns for low context overhead & speed
        if len(self.messages) > 7:
            self.messages = [self.system_prompt] + self.messages[-6:]
            
        t_start = time.time()
        try:
            # Generate short, crisp conversational response with low max_new_tokens for low latency
            result = self.generator(
                self.messages, 
                max_new_tokens=45, 
                temperature=0.6,
                do_sample=True,
                pad_token_id=self.generator.tokenizer.eos_token_id
            )
            generated_messages = result[0]["generated_text"]
            reply = generated_messages[-1]["content"].strip()
            
            # Clean any stray formatting
            reply = reply.replace("*", "").replace("#", "").strip()
            
            self.messages.append({"role": "assistant", "content": reply})
            latency = round(time.time() - t_start, 3)
            return reply, latency
        except Exception as e:
            print(f"Error generating text: {e}")
            latency = round(time.time() - t_start, 3)
            return "I'm having a little trouble thinking right now. Could you repeat that?", latency
    
    def reset_context(self):
        """
        Clears the conversation history to start fresh.
        """
        self.messages = [self.system_prompt]
