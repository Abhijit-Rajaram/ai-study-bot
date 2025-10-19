# 📚 Study Bot (Mistral + ChromaDB + FastAPI)

A personalized AI study assistant that lets you **upload PDFs**, **store their content**, and **ask questions** about your notes. It uses **retrieval-augmented generation (RAG)** with **ChromaDB embeddings** and an **LLM (Mistral via Ollama)**.

---

## Features

- **PDF Upload:** Upload text-based PDFs; content is split into chunks and stored in ChromaDB.
- **Semantic Search:** Retrieves the most relevant chunks based on your question using vector embeddings.
- **AI Answers:** Generates answers using Mistral based on retrieved content.
- **Persistent Storage:** Stores chat history and uploaded PDF metadata in a database (SQLite/PostgreSQL) yet to implement.
- **Web Interface:** Responsive Bootstrap UI with tabs for Chat and Uploaded Files.
- **Token & Cost Optimization:** Supports top-k retrieval and summarization to reduce token usage if using cloud APIs.

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/Abhijit-Rajaram/ai-study-bot.git
cd study-bot
```
## Step 2: Create a Python Virtual Environment

To isolate your project dependencies and avoid conflicts, create a virtual environment:

```bash
# Create a virtual environment named 'venv'
python -m venv venv

# Activate the environment
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

## Step 3: Install Python Dependencies

After activating your virtual environment, install all required Python packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Install Ollama

1. Download and install **Ollama** from [https://ollama.com](https://ollama.com) and follow the installer instructions for your operating system (Windows, Mac, or Linux).

2. Verify the installation by running:

```bash
ollama --version

ollama pull mistral

ollama serve # if required
```

## Step 5: Configure Database

- **SQLite (Default)**
  - Stores chat history and uploaded PDF metadata.
  - Database file: `studybot.db`.
  - Ensures persistence of user interactions and uploaded files locally.

- **ChromaDB**
  - Stores vector embeddings for PDF chunks.
  - Persistent folder: `chroma_data/`.
  - Enables semantic search to retrieve relevant content efficiently.

- **Optional: Cloud Database**
  - You can use PostgreSQL, Supabase, or another cloud database.
  - Update your database connection string in `models.py` if switching from SQLite.
  - Useful for multi-user support or cloud deployment.

## Step 6: Run the FastAPI Application

Run the FastAPI backend using `uvicorn`:

```bash
uvicorn main:app --reload
```

## Step 7: Upload PDFs

1. Navigate to the **"Uploads" tab** in the web interface.
2. Select a **text-based PDF** from your computer.
3. Click the **Upload PDF** button.
4. The bot will:
   - Extract text using PyMuPDF (`fitz`).
   - Split the text into **semantic chunks** (e.g., 1000 characters per chunk).
   - Store the embeddings in **ChromaDB**.
   - Delete the original PDF file after processing.
5. After successful upload, you will see a confirmation message indicating how many chunks were added.

## Step 8: Ask Questions

1. Switch to the **"Chat" tab** in the web interface.
2. Type your question in the input box and click **Send**.
3. The bot will:
   - Retrieve the **top-k most relevant chunks** from ChromaDB.
   - Generate an answer using **Mistral** (local) or **GPT-3.5** (cloud) based on the retrieved context.
   - Display the response in the chatbox under your message.
4. The conversation history is appended below, allowing you to follow previous interactions.


## Project Structure

- **study-bot/**  
  - **main.py** – FastAPI backend with routes for chat and PDF upload  
  - **models.py** – Database models for chat history and uploaded PDFs  
  - **templates/** – HTML files  
    - **index.html** – Main HTML UI (Bootstrap + JavaScript)  
  - **uploads/** – Temporary storage for uploaded PDFs  
  - **chroma_data/** – Persistent ChromaDB vector embeddings  
  - **studybot.db** – SQLite database file  
  - **requirements.txt** – Python dependencies  
  - **README.md** – Project documentation
