# Pet Care Coach — RAG Demo Application

A comprehensive demonstration of Retrieval-Augmented Generation (RAG) evolution, showcasing three levels of context sophistication: **Model-only**, **Classic RAG**, and **Agentic Context**. Built with Streamlit and OpenAI, this application demonstrates how better context systems lead to better answers.

## 🎯 Purpose

This application is designed as an educational demo to **visibly demonstrate** the difference between:

1. **Model-only (No RAG)** — Guessing in the dark  
   The assistant answers based only on general knowledge, with no access to specific context.

2. **Classic RAG (Transcript)** — Remembering what was said  
   The assistant can search and retrieve information from visit transcripts using semantic search.

3. **Agentic Context (Transcript + Diagnostics)** — Reasoning across evidence  
   The assistant can search transcripts **and** query structured diagnostic data, iteratively gathering evidence to provide grounded answers.

**Key Message:** Better answers aren't just better prompts. They're better **context systems**.

## 🚀 Features

### Core Capabilities
- **Three Chat Modes**: Switch between Model-only, Classic RAG, and Agentic Context
- **Document Upload**: Upload markdown visit transcripts and automatically chunk them
- **Semantic Search**: Use OpenAI embeddings to find relevant document chunks
- **SQLite Diagnostics Database**: Structured storage for lab results, tests, and visit data
- **Agentic Orchestration**: Intelligent tool selection and iterative evidence gathering
- **Transparency**: "How I answered" panels show tools used, citations, SQL queries, and confidence levels

### Agentic Context Features
- **Dual Tool System**: 
  - `search_transcripts()` — Semantic search over visit transcripts
  - `query_diagnostics()` — SQL queries over structured diagnostic data
- **Intelligent Tool Selection**: Automatically chooses which tools to use based on the question
- **Iterative Retrieval**: Can refine queries and gather additional evidence (up to 3 iterations)
- **SQL Safety**: Read-only queries with keyword blocking and LIMIT enforcement
- **Evidence Tracking**: Full trace of tools used, queries executed, and results retrieved

### Diagnostics Viewer
- Browse visits, tests, and results
- View abnormal lab values
- See full diagnostic panels (CBC, Chemistry, etc.)

## 🏗️ Architecture

### Project Structure
```
rag_hello_world/
├── app.py                      # Main Streamlit application
├── rag_utils.py                # RAG utilities (chunking, embedding, search)
├── rag_store.json              # Document store (chunks + embeddings)
├── agentic/
│   ├── agentic.py             # Agentic orchestrator
│   ├── tools.py               # Tool implementations (search, SQL)
│   └── sql_safety.py          # SQL safety checks
├── diagnostics/
│   ├── schema.sql             # Database schema
│   ├── db.py                  # Database initialization
│   ├── queries.py             # Helper queries for viewer
│   └── seed.py                # Demo data seeding
├── sample_docs/
│   ├── demo.md                # Basic RAG demo document
│   └── visit_transcript_daisy.md  # Sample visit transcript
└── docs/
    └── pet-care-coach-agentic-rag-design.md  # Design documentation
```

### Key Components

**RAG System** (`rag_utils.py`)
- Document chunking with overlap
- OpenAI embedding generation
- Cosine similarity search
- JSON-based document store

**Agentic System** (`agentic/`)
- Tool selection logic
- Iterative retrieval loop
- Evidence assembly
- Confidence assessment

**Diagnostics Database** (`diagnostics/`)
- SQLite database with realistic veterinary schema
- Views for easier NL→SQL queries
- Seed data for demo scenarios

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Internet connection for API calls

## 🛠️ Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd rag_hello_world
   ```

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

1. **Start the application**:
   ```bash
   streamlit run app.py
   ```

2. **Load demo data**:
   - Click "Load Seed Data" in the sidebar to populate the diagnostics database
   - Upload `sample_docs/visit_transcript_daisy.md` to add the visit transcript

3. **Try the three modes**:
   - **Model-only**: "My dog is vomiting. What could it be?"
   - **Classic RAG**: "What did the vet recommend we do at home?"
   - **Agentic Context**: "Which lab values were abnormal and what might they indicate?"

## 📖 Usage Guide

### Mode Selection

Choose your mode from the sidebar:

#### 1. Model-only (No RAG)
- Answers based purely on the model's training data
- No access to specific documents or data
- Best for: Demonstrating limitations of context-free responses

**Example Questions:**
- "My dog is vomiting and lethargic. What could it be?"
- "What are common causes of elevated BUN in dogs?"

#### 2. Classic RAG (Transcript)
- Searches uploaded visit transcripts using semantic search
- Retrieves relevant chunks and grounds answers in them
- Best for: Questions about what was discussed, recommendations, symptoms

**Example Questions:**
- "What did the vet recommend we do at home after the visit?"
- "What were Daisy's symptoms?"
- "Summarize the visit and draft SOAP notes."

#### 3. Agentic Context (Transcript + Diagnostics)
- Can search transcripts **and** query structured diagnostic data
- Intelligently selects tools based on the question
- Iteratively gathers evidence (up to 3 tool calls)
- Shows full transparency: tools used, queries executed, confidence level

**Example Questions:**
- "Which lab values were abnormal and what might they indicate?"
- "What are the most recent CBC test results for Daisy?"
- "Do the lab results support dehydration? Show me the evidence."
- "What follow-up tests did the vet mention, and do the lab results suggest urgency?"

### Document Management

**Upload Documents:**
- Use the sidebar file uploader to add markdown (`.md`) or text (`.txt`) files
- Documents are automatically chunked and embedded
- View the number of indexed chunks in the sidebar

**Clear Document Store:**
- Click "Clear document store" to remove all indexed documents
- Useful when testing with different document sets

### Diagnostics Database

**Load Seed Data:**
- Click "Load Seed Data" to populate the database with demo data
- Includes: Owner (Alex Morgan), Pet (Daisy), Visit, Tests (CBC, Chemistry Panel), Results

**View Diagnostics:**
- Check "Show Diagnostics Viewer" to browse the database
- Select a visit to see tests, results, and abnormal values

**Clear Database:**
- Click "Clear Diagnostics Database" to remove all data

### Understanding Agentic Responses

When using Agentic Context mode, each response includes a "🔍 How I answered" expandable panel showing:

- **Mode**: Agentic Context
- **Confidence**: High/Medium/Low with reasoning
- **Retrieved Transcript Chunks**: Source documents with similarity scores
- **SQL Queries Executed**: The actual SQL queries run against the database
- **SQL Results**: Preview of returned data
- **Trace**: Full step-by-step decision log

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | Your OpenAI API key |
| `RAG_STORE_PATH` | `rag_store.json` | Path to the document store file |
| `DIAGNOSTICS_DB_PATH` | `diagnostics/diagnostics.db` | Path to SQLite database |
| `CHAT_MODEL` | `gpt-4o-mini` | OpenAI model for chat completions |
| `EMBED_MODEL` | `text-embedding-3-small` | OpenAI model for embeddings |
| `AGENT_MAX_TOOL_CALLS` | 3 | Maximum tool calls per agentic query |
| `SQL_MAX_ROWS` | 50 | Maximum rows returned from SQL queries |

### Application Settings

**Sidebar Controls:**
- **Top-k chunks**: Number of document chunks to retrieve (1-8, default: 4)
- **Chat model**: OpenAI model selection (default: `gpt-4o-mini`)

**Agentic Settings** (hardcoded, can be modified in `agentic/agentic.py`):
- **Max tool calls**: 3 iterations
- **SQL max rows**: 50 rows per query
- **Top-k retrieval**: Configurable via sidebar

## 🔧 Technical Details

### Document Chunking
- **Chunk Size**: 1000 characters (configurable in `rag_utils.py`)
- **Overlap**: 150 characters between chunks
- **Method**: Paragraph-based with character-based fallback for long paragraphs
- **Supported Formats**: Markdown (`.md`), Text (`.txt`)

### Embedding & Search
- **Embedding Model**: OpenAI `text-embedding-3-small`
- **Similarity Metric**: Cosine similarity
- **Storage**: Local JSON file (`rag_store.json`)

### RAG Pipeline
1. **Query Processing**: User question is embedded
2. **Retrieval**: Top-k most similar chunks are found using cosine similarity
3. **Context Assembly**: Retrieved chunks are formatted with citations
4. **Generation**: LLM generates response using context + query

### Agentic Pipeline
1. **Clarification Check**: Determines if question is clear enough to proceed
2. **Tool Selection**: Chooses which tools to use (SQL, docs, or both)
3. **Tool Execution**: 
   - Generates SQL queries (if needed)
   - Searches transcripts (if needed)
4. **Iteration**: Refines queries if evidence is insufficient (up to 3 times)
5. **Answer Composition**: Combines evidence from all tools
6. **Confidence Assessment**: Evaluates answer quality based on evidence

### SQL Safety
The `query_diagnostics()` tool includes multiple safety layers:
- **Read-only enforcement**: Only `SELECT` statements allowed
- **Keyword blocking**: Blocks `DROP`, `DELETE`, `UPDATE`, `INSERT`, etc.
- **LIMIT enforcement**: Automatically adds `LIMIT 50` if missing
- **Single statement**: Prevents multiple statements in one query

### Database Schema
The diagnostics database includes:
- **Core entities**: Owners, Pets, Visits
- **Diagnostics**: Tests, Analytes, Reference Ranges, Test Results
- **Views**: `v_results` for easier NL→SQL queries

See `diagnostics/schema.sql` for full schema details.

## 🐛 Troubleshooting

### Common Issues

**"Set the OPENAI_API_KEY environment variable"**
- Ensure your API key is properly set in your environment
- Restart the application after setting the variable

**"No documents in store or no matches"**
- Upload some markdown files first
- Check that your question relates to the uploaded content

**Agentic mode asks for clarification unnecessarily**
- The clarification check has been tuned, but may still be conservative
- Try rephrasing questions to be more explicit (e.g., "Show me Daisy's CBC results")

**SQL queries return no results**
- Verify seed data is loaded
- Check that pet names match exactly (case-sensitive)
- Try simpler queries first to verify database connectivity

**Empty responses or errors**
- Verify your OpenAI API key has sufficient credits
- Check your internet connection
- Try a different model if the default isn't working

### Performance Tips

- Use smaller chunk sizes for more precise retrieval
- Adjust top-k based on your document size and query complexity
- Clear the document store periodically if you're testing with many files
- For agentic mode, simpler questions often work better than complex multi-part queries

## 📚 Example Workflows

### Basic RAG Demo
1. Upload `sample_docs/demo.md`
2. Switch to "Classic RAG (Transcript)" mode
3. Ask: "What is RAG?"
4. Compare with "Model-only" mode to see the difference

### Full Agentic Demo
1. Load seed data (click "Load Seed Data")
2. Upload `sample_docs/visit_transcript_daisy.md`
3. Switch to "Agentic Context (Transcript + Diagnostics)" mode
4. Try these questions in order:
   - "What are the most recent CBC test results for Daisy?"
   - "Which lab values were abnormal?"
   - "What did the vet recommend, and do the lab results support that recommendation?"
5. Expand "🔍 How I answered" to see the full trace

### Comparing All Three Modes
Ask the same question in each mode:
- **Question**: "What could be causing Daisy's symptoms?"
- **Model-only**: General knowledge about vomiting in dogs
- **Classic RAG**: Information from the visit transcript
- **Agentic Context**: Combines transcript + specific lab values

## 🎓 Educational Use

This application is designed for teaching and demonstration purposes. It showcases:

- **Context Evolution**: From no context → unstructured context → structured + unstructured context
- **Tool Use**: How agents can select and use multiple tools
- **Transparency**: Making AI reasoning visible through traces and evidence
- **Safety**: SQL injection prevention and read-only database access
- **Practical Application**: Real-world scenario (veterinary clinic) that's easy to understand

## 🤝 Contributing

This is a classroom demo project. Feel free to:
- Experiment with different chunking strategies
- Try different embedding models
- Add support for more document formats
- Implement more sophisticated retrieval methods
- Extend the agentic tools (e.g., add a clarifier tool for visit selection)

## 📄 License

This project is for educational purposes. Please ensure you comply with OpenAI's usage policies when using their APIs.

## 🙏 Acknowledgments

This project demonstrates concepts from:
- Retrieval-Augmented Generation (RAG)
- Agentic AI systems
- Tool use and orchestration
- Context systems design

---

**Remember**: Better answers aren't just better prompts. They're better **context systems**.
