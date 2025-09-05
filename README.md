
# RAG Hello World — Streamlit + OpenAI

A minimal Retrieval-Augmented Generation (RAG) demo application built with Streamlit and OpenAI. This project demonstrates how to build a simple RAG system that can upload documents, create embeddings, and answer questions using both general knowledge and retrieved document context.

## 🚀 Features

- **Document Upload**: Upload markdown files and automatically chunk them for processing
- **Semantic Search**: Use OpenAI embeddings to find relevant document chunks
- **RAG vs Model-Only Comparison**: Toggle between RAG-grounded answers and pure model responses
- **Interactive Chat Interface**: Clean Streamlit-based chat interface
- **Citation Support**: View retrieved sources with similarity scores
- **Configurable Parameters**: Adjust top-k retrieval, model selection, and other settings
- **Local JSON Storage**: Simple file-based document store (no database required)

## 🏗️ Architecture

The application consists of two main components:

### Core Files
- **`app.py`**: Main Streamlit application with chat interface and document management
- **`rag_utils.py`**: RAG utilities for document processing, embedding, and search
- **`rag_store.json`**: Local JSON file storing document chunks and embeddings

### Key Functions
- **Document Processing**: Chunks markdown documents with configurable size and overlap
- **Embedding Generation**: Uses OpenAI's `text-embedding-3-small` model
- **Similarity Search**: Cosine similarity-based retrieval of relevant chunks
- **Context Assembly**: Combines retrieved chunks with user queries for grounded responses

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Internet connection for API calls

## 🛠️ Installation

1. **Clone or download the project**
2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up your OpenAI API key**:
   ```bash
   export OPENAI_API_KEY=sk-your-api-key-here  # On Windows: set OPENAI_API_KEY=sk-your-api-key-here
   ```

## 🚀 Quickstart

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

## 📖 Usage

### 1. Upload Documents
- Use the sidebar to upload markdown (`.md`) or text (`.txt`) files
- Documents are automatically chunked and embedded
- View the number of indexed chunks in the sidebar

### 2. Configure Settings
- **Use RAG retrieval**: Toggle to compare RAG vs model-only responses
- **Top-k chunks**: Adjust how many document chunks to retrieve (1-8)
- **Chat model**: Select the OpenAI model (default: `gpt-4o-mini`)

### 3. Ask Questions
- Type questions in the chat interface
- With RAG enabled, answers will be grounded in your uploaded documents
- View retrieved sources in the expandable section below responses

### 4. Compare Responses
- Toggle RAG on/off to see the difference between:
  - **RAG responses**: Grounded in your documents with citations
  - **Model-only responses**: Based purely on the model's training data

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | Your OpenAI API key |
| `RAG_STORE_PATH` | `rag_store.json` | Path to the document store file |
| `CHAT_MODEL` | `gpt-4o-mini` | OpenAI model for chat completions |
| `EMBED_MODEL` | `text-embedding-3-small` | OpenAI model for embeddings |

### Document Processing Settings

- **Chunk Size**: 1000 characters (configurable in `rag_utils.py`)
- **Overlap**: 150 characters between chunks
- **Supported Formats**: Markdown (`.md`), Text (`.txt`)

## 🔧 Technical Details

### Document Chunking
Documents are split into overlapping chunks using paragraph boundaries, with fallback to character-based splitting for long paragraphs.

### Embedding & Search
- Uses OpenAI's embedding API to create vector representations
- Implements cosine similarity for semantic search
- Stores embeddings locally in JSON format

### RAG Pipeline
1. **Query Processing**: User question is embedded
2. **Retrieval**: Top-k most similar chunks are found
3. **Context Assembly**: Retrieved chunks are formatted with citations
4. **Generation**: LLM generates response using context + query

## 🐛 Troubleshooting

### Common Issues

**"Set the OPENAI_API_KEY environment variable"**
- Ensure your API key is properly set in your environment
- Restart the application after setting the variable

**"No documents in store or no matches"**
- Upload some markdown files first
- Check that your question relates to the uploaded content

**Empty responses or errors**
- Verify your OpenAI API key has sufficient credits
- Check your internet connection
- Try a different model if the default isn't working

### Performance Tips

- Use smaller chunk sizes for more precise retrieval
- Adjust top-k based on your document size and query complexity
- Clear the document store periodically if you're testing with many files

## 📚 Example Workflow

1. Upload the included `sample_docs/demo.md` file
2. Ask: "What is RAG?"
3. Compare responses with RAG enabled vs disabled
4. Notice how RAG responses include citations to your uploaded document

## 🤝 Contributing

This is a classroom demo project. Feel free to:
- Experiment with different chunking strategies
- Try different embedding models
- Add support for more document formats
- Implement more sophisticated retrieval methods

## 📄 License

This project is for educational purposes. Please ensure you comply with OpenAI's usage policies when using their APIs.
