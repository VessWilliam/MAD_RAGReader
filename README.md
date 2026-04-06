## MAD RAG Reader 🧸

A doc-base AI Chat Systems That answers base from PDF using RAG & Streaming LLM.

## Tech Stack 
- 🐍 Python 3.12
- ⚡ Backend: FastAPI
- 🖼️ Frontend:Streamlit
- 🤖 LLM: Groq (Qwen3-32B)
- 👾 Vector Store: FAISS
- 🗃️ Database: SQLite
- 📦 Runtime: Poetry
- 🐋 Container: Docker
- 🧪 Pytest : testing

      🧠 System Flow
      
      User
        ↓
      Streamlit (Frontend)
        ↓
      FastAPI (Backend)
           ├── FAISS (PDF Retrieval)
           ├── SQLite (Chat History)
           └── LLM (Groq)

## Test Result 
    ##  poetry run pytest -v
    <img width="1597" height="196" alt="image" src="https://github.com/user-attachments/assets/57961cdc-e20d-4d3f-8922-4c2094deacab" />

## Run Docker Compose 
    ## cd .\docker\
    ## docker-compose up --build 


