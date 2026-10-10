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
            "content": "You are Aura, a helpful and concise voice AI assistant. Keep your answers brief (1-2 sentences), natural, and conversational, as they will be spoken out loud. Avoid using lists, markdown formatting, or overly complex sentences."
        }
        self.messages = [self.system_prompt]
        
    def chat(self, user_text):
        """
        Sends the user text to the LLM and returns the response, maintaining context.
        """
        self.messages.append({"role": "user", "content": user_text})
        
        try:
            # Generate response
            result = self.generator(self.messages, max_new_tokens=60, temperature=0.7)
            # Pipeline returns the full conversation when passing messages
            generated_messages = result[0]["generated_text"]
            # The last message is the assistant's reply
            reply = generated_messages[-1]["content"]
            
            self.messages.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            print(f"Error generating text: {e}")
            return "I'm sorry, my language model encountered an error."
    
    def reset_context(self):
        """
        Clears the conversation history to start fresh.
        """
        self.messages = [self.system_prompt]
