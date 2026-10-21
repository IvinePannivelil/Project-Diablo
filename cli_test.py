import sys
from core.memory import RAGMemory

print("=== DIABLO TEXT-ONLY FALLBACK MODE ===")
print("Loading memory...")

try:
    memory = RAGMemory()
except Exception as e:
    print(f"Failed to load memory: {e}")
    sys.exit(1)

print("\nDiablo is online. (LLM and Voice bypassed for pure CLI testing).")
print("Type 'exit' to quit.")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == 'exit':
        break
    
    print("Diablo [Internal]: Searching memory...")
    
    results = memory.search(user_input)
    if results:
        context = " ".join(results)
        print(f"Diablo: I found this in your files: {context}")
    else:
        print("Diablo: I have no memory of this topic.")

