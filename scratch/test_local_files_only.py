from sentence_transformers import SentenceTransformer

model_name = "all-MiniLM-L6-v2"
print(f"Testing loading model '{model_name}' with local_files_only=True...")

try:
    model = SentenceTransformer(model_name, local_files_only=True)
    print("SUCCESS: Local cached model loaded cleanly with local_files_only=True!")
except Exception as e:
    print(f"NOT CACHED LOCALLY: {type(e).__name__}: {e}")
    print("Falling back to local_files_only=False...")
    model = SentenceTransformer(model_name, local_files_only=False)
    print("SUCCESS: Downloaded/loaded model with local_files_only=False!")
