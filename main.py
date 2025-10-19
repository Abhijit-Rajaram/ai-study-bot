from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import subprocess, json, os, fitz
import chromadb
from chromadb.utils import embedding_functions
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


# --- Setup ---
app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
# --- Initialize ChromaDB (persistent) ---
chroma_client = chromadb.PersistentClient(path="chroma_data")
collection = chroma_client.get_or_create_collection(name="study_material")

embedding_func = embedding_functions.DefaultEmbeddingFunction()

# --- Helper: Run Mistral via Ollama ---
def run_mistral(prompt: str) -> str:
    import subprocess
    print(f"{prompt=}")
    try:
        result = subprocess.run(
            ["ollama", "run", "mistral"],  # just run without flags
            input=prompt.encode('utf-8'),  # encode prompt as UTF-8
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # timeout=60
        )

        # decode stdout/stderr safely as UTF-8
        stdout = result.stdout.decode('utf-8', errors='ignore').strip()
        stderr = result.stderr.decode('utf-8', errors='ignore').strip()

        if "requires more system memory" in stderr.lower():
            return ("Error: Not enough memory to run Mistral. "
                    "Close other programs or reduce context size.")

        if result.returncode != 0:
            return f"Error: Ollama returned an error. Details: {stderr}"

        return stdout if stdout else "No response from model."

    except subprocess.TimeoutExpired:
        return "Error: Mistral request timed out."
    except Exception as e:
        return f"Unexpected error: {e}"




# --- Helper: Extract text from PDF ---
def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content from a PDF.
    - If a page contains text, extract it.
    - If a page is image-only (no text layer), skip it.
    - Does not perform OCR — images are ignored.
    """
    text_content = []
    doc = fitz.open(file_path)

    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        if text.strip():
            text_content.append(text)
        else:
            # Just log skipped pages for reference
            print(f"ℹ️ Page {page_num + 1} has no text — likely image-based. Skipping...")

    doc.close()
    return "\n".join(text_content)


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Upload PDF -> Extract -> Store in ChromaDB -> Delete PDF
@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text_from_pdf(file_path)
    if not text.strip():
        os.remove(file_path)
        return JSONResponse({"status": "error", "message": "No readable text found in PDF."})

    # Split text into manageable chunks for embedding
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    ids = [f"{file.filename}_chunk_{i}" for i in range(len(chunks))]

    # Store embeddings in ChromaDB
    collection.add(documents=chunks, ids=ids)

    # Delete the uploaded PDF after successful storage
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Warning: Could not delete file {file_path}: {e}")

    return JSONResponse({
        "status": "ok",
        "message": f"Added {len(chunks)} chunks from {file.filename} and deleted the original file."
    })

# Chat with retrieval from ChromaDB
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message")

    # Retrieve most relevant notes
    results = collection.query(query_texts=[user_message], n_results=3)
    retrieved_context = "\n".join(results["documents"][0]) if results["documents"] else ""

    prompt = f"""You are a helpful study assistant.
Use the context below to answer the question as accurately as possible.

Context:
{retrieved_context}

Question:
{user_message}
"""

    response = run_mistral(prompt)
    return JSONResponse({"reply": response})
