import os
from llama_cpp import Llama

class LocalLLM:
    def __init__(self, model_path: str = "models/model.gguf"):
        self.model_path = model_path
        self.llm = None
        
    def load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at {self.model_path}. Please place a .gguf model here.")
        
        print("Loading local AI model to RTX 4060...")
        self.llm = Llama(
            model_path=self.model_path,
            n_gpu_layers=-1, # Offload to GPU
            n_ctx=4096,
            verbose=False
        )
        print("Model loaded successfully.")
        
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        if not self.llm:
            self.load_model()
            
        output = self.llm(
            prompt,
            max_tokens=max_tokens,
            stop=["User:", "\n\n"],
            echo=False
        )
        return output['choices'][0]['text'].strip()

