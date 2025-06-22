import shutil
import os

CHROMA_PATH = "../embeddings/chroma_db"

if os.path.exists(CHROMA_PATH):
    shutil.rmtree(CHROMA_PATH)
    print(f"✅ ChromaDB at '{CHROMA_PATH}' deleted.")
else:
    print(f"❌ ChromaDB directory '{CHROMA_PATH}' does not exist.")