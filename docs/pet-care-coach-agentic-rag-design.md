# Promptly-at-9 Demo Upgrade Design — “Pet Care Coach” (No RAG → Classic RAG → Agentic Context)

> Target repo: `https://github.com/terrytompkins/rag_hello_world`  
> Target app: Streamlit “RAG Hello World” demo, extended to support a third mode (“Agentic Context”) using SQLite diagnostics + tool-driven orchestration.  
> Audience goal: a single live demo that **visibly** demonstrates the difference between:
> 1) **Model-only chat** (no context beyond the prompt),  
> 2) **Classic RAG** (unstructured “visit transcript” memory), and  
> 3) **Agentic Context** (unstructured transcript **plus** structured diagnostics + tool use + iterative retrieval).

---

## 1) Narrative framing for the session

Use these three stages as the story:

1. **Before the clinic (Guessing in the dark)**  
   The pet owner uses a general AI chat to ask what might be wrong based only on symptoms.

2. **After the visit (Remembering what was said)**  
   The clinic system transcribes the visit, ingests it into a vector store, and the vet uses RAG to recall the conversation and create notes.

3. **During treatment (Reasoning across evidence)**  
   The clinic has diagnostic instruments; results are stored in a database. The assistant can **retrieve transcript context** *and* **query diagnostics** (and optionally other tools) to generate grounded treatment guidance or next-step recommendations.

Key message (non-technical-friendly):  
> “Better answers aren’t just better prompts. They’re better **context systems**.”

---

## 2) What we’re adding

### Existing (already in repo)
- Streamlit chat UI
- Toggle for RAG on/off
- Document ingestion (markdown/text) → chunking → embeddings → local store (JSON)
- Retrieval + citations display

### New
- **SQLite diagnostics database** with a realistic schema
- **Agentic mode** that can:
  - Ask a clarifying question when needed
  - Choose tools (docs search vs SQL)  
  - Iterate retrieval (loop) up to a hard cap  
  - Produce an answer with evidence (citations + SQL snippet) and confidence
- **Simple diagnostic data viewer**
  - Built into Streamlit (recommended for simplicity)  
  - Optional external viewer (DB Browser / Datasette) for “peek under the hood”

---

## 3) UX / UI changes in Streamlit

### Sidebar
Add a **Mode selector** (radio):
- **Model-only (No RAG)**
- **Classic RAG (Transcript)**
- **Agentic Context (Transcript + Diagnostics)**

Keep (or adapt) existing controls:
- Model dropdown (chat model)
- RAG retrieval `top_k`
- “Upload / ingest docs” section (used for transcript doc ingestion)
- “Clear chat” button

### Main panel
- Chat transcript as-is (st.chat_message)
- For each assistant response, add an expandable **“How I answered”** panel:
  - Mode used
  - Tools invoked (in agentic mode)
  - Retrieved doc chunk citations (if any)
  - SQL query (sanitized) + top rows (if any)
  - Confidence level and why

### Optional: Diagnostics viewer tab (recommended)
Add a Streamlit “page” or in-app section:
- “Diagnostics Viewer”
  - pick a `visit_id` (or pet name)
  - show summary tables:
    - visit info
    - tests performed
    - result rows with reference ranges

> If your app is currently single-page, keep it simple: add a sidebar checkbox “Show Diagnostics Viewer” that reveals a read-only viewer under the chat.

---

## 4) SQLite schema (realistic enough for NL→SQL)

### Design principles
- Realistic entities: owners, pets, visits, tests, analytes, results
- Reference ranges per species (optionally breed/age)
- Values + units + flags (H/L) to support clinical-style reasoning
- A small amount of metadata (timestamps, specimen type) so queries can be natural

### Proposed tables (DDL)

Create a folder: `diagnostics/` with a `schema.sql`:

```sql
PRAGMA foreign_keys = ON;

-- --- Core entities ---
CREATE TABLE IF NOT EXISTS owners (
  owner_id        TEXT PRIMARY KEY,
  full_name       TEXT NOT NULL,
  phone           TEXT,
  email           TEXT
);

CREATE TABLE IF NOT EXISTS pets (
  pet_id          TEXT PRIMARY KEY,
  owner_id        TEXT NOT NULL REFERENCES owners(owner_id),
  name            TEXT NOT NULL,
  species         TEXT NOT NULL,        -- e.g., Dog, Cat
  breed           TEXT,
  sex             TEXT,                 -- M, F, MN, FN
  date_of_birth   TEXT,                 -- ISO date
  weight_kg       REAL
);

CREATE TABLE IF NOT EXISTS visits (
  visit_id        TEXT PRIMARY KEY,
  pet_id          TEXT NOT NULL REFERENCES pets(pet_id),
  clinic_name     TEXT NOT NULL,
  visit_datetime  TEXT NOT NULL,        -- ISO datetime
  chief_complaint TEXT,
  notes           TEXT
);

-- --- Diagnostics orders / panels ---
CREATE TABLE IF NOT EXISTS tests (
  test_id         TEXT PRIMARY KEY,
  visit_id        TEXT NOT NULL REFERENCES visits(visit_id),
  test_name       TEXT NOT NULL,        -- e.g., "CBC", "Chemistry Panel", "Urinalysis"
  specimen_type   TEXT,                 -- e.g., Blood, Serum, Urine
  ordered_datetime TEXT,
  result_datetime  TEXT,
  status          TEXT                  -- e.g., Final
);

-- --- Individual analytes in a test (e.g., ALT, AST, WBC) ---
CREATE TABLE IF NOT EXISTS analytes (
  analyte_id      TEXT PRIMARY KEY,
  analyte_code    TEXT NOT NULL,        -- e.g., ALT, BUN, WBC
  analyte_name    TEXT NOT NULL,
  unit            TEXT NOT NULL
);

-- Reference ranges can vary by species (and optionally age group)
CREATE TABLE IF NOT EXISTS reference_ranges (
  range_id        TEXT PRIMARY KEY,
  species         TEXT NOT NULL,        -- Dog/Cat
  analyte_id      TEXT NOT NULL REFERENCES analytes(analyte_id),
  low_value       REAL,
  high_value      REAL,
  notes           TEXT
);

-- Results: one row per analyte per test
CREATE TABLE IF NOT EXISTS test_results (
  result_id       TEXT PRIMARY KEY,
  test_id         TEXT NOT NULL REFERENCES tests(test_id),
  analyte_id      TEXT NOT NULL REFERENCES analytes(analyte_id),
  value_num       REAL,                 -- numeric value when applicable
  value_text      TEXT,                 -- for qualitative results (e.g., "Negative")
  unit            TEXT NOT NULL,        -- duplicated for convenience / display
  flag            TEXT,                 -- H, L, N, or NULL
  comment         TEXT
);

-- Helpful views (optional) for easier reporting / NL queries
CREATE VIEW IF NOT EXISTS v_results AS
SELECT
  v.visit_id,
  v.visit_datetime,
  p.name AS pet_name,
  p.species,
  t.test_id,
  t.test_name,
  a.analyte_code,
  a.analyte_name,
  r.value_num,
  r.value_text,
  r.unit,
  r.flag
FROM test_results r
JOIN tests t     ON t.test_id = r.test_id
JOIN visits v    ON v.visit_id = t.visit_id
JOIN pets p      ON p.pet_id = v.pet_id
JOIN analytes a  ON a.analyte_id = r.analyte_id;
```

### Notes
- The `v_results` view makes NL→SQL far easier (“show all abnormal results for Daisy’s last visit”).
- For the demo, keep scope to **one pet + one visit** initially, then add 1–2 more visits to demonstrate time-series questions.

---

## 5) Seed data plan (we’ll fabricate after wiring)

Create `diagnostics/seed.py` (or `seed.sql`) later, but plan for:

- 1 owner: “Alex Morgan”
- 1 dog: “Daisy” (Dog, mixed breed, ~6 years old, 18.2 kg)
- 1 visit: vomiting + lethargy + decreased appetite
- Tests:
  - CBC
  - Chemistry panel
  - Optional: urinalysis

Results should contain:
- A few normals
- A couple meaningful abnormalities (enough to support “why” questions)

Examples of analytes to include:
- CBC: WBC, Neutrophils, HCT/PCV, Platelets
- Chem: BUN, Creatinine, ALT, ALP, Glucose, Total Protein, Albumin, Globulin, Sodium, Potassium, Chloride
- UA (optional): Specific gravity, ketones, glucose, protein

---

## 6) Agentic Context: tools + orchestration

### The minimum tool set (recommended)
1) **Docs search tool**: searches the transcript doc store (existing RAG)
2) **SQL query tool**: queries SQLite diagnostics

Everything else is optional.

### Tool interface (Python “tools”)
Create `agent_tools.py` (or `diagnostics/tools.py`) with two functions:

- `search_transcripts(query: str, top_k: int) -> dict`
  - returns: list of `{chunk_id, text, score, source_doc}`
  - Uses your existing retrieval function(s) in `rag_utils.py`

- `query_diagnostics(sql: str) -> dict`
  - returns: `{columns: [...], rows: [...], row_count: int}`
  - Executes read-only SQL against SQLite
  - Hard safety:
    - only allow `SELECT` statements
    - deny `PRAGMA`, `ATTACH`, `DROP`, `INSERT`, etc.
    - optionally enforce a max row limit (e.g., `LIMIT 50`)

### Agent loop (high-level)
Add `agentic.py` with a single function:

`run_agentic_chat(user_msg, chat_history, rag_store, sqlite_path, config) -> AgenticResponse`

Where `AgenticResponse` includes:
- `final_answer` (string)
- `evidence`:
  - retrieved_chunks (list)
  - sql_queries (list)
  - sql_results (small preview)
- `trace` (steps used, decisions, confidence)

#### Suggested loop behavior
- Max tool calls: **3** (hard cap)
- Step 0: Determine whether clarification is needed
  - If missing key info (pet name, visit, timeframe), ask **one** clarifying question and stop.
- Step 1: Decide which tool(s) to use first
  - If question mentions “lab values / test results / abnormal / ALT / WBC / last visit results” → use SQL first
  - If question mentions “what did the vet say / symptoms / advice / discharge instructions” → docs first
  - If question is “what does this lab mean?” → both
- Step 2: Evaluate sufficiency
  - If evidence weak/empty → refine query and try once more (loop)
- Step 3: Compose answer
  - Include citations (doc chunks) and/or “Based on lab results…” with a brief table snippet
  - Provide “Confidence: High/Medium/Low” and why

### Prompting strategy for the agent (Cursor-friendly)
Use a system prompt for agentic mode along these lines:

- You are a veterinary clinic assistant for demo purposes only.
- You must ground answers in:
  - transcript excerpts (when available)
  - diagnostic data (when available)
- If you cannot find evidence, say so and ask for what you need.
- Use tools to gather evidence; do not invent lab values.
- When generating SQL:
  - use only tables/views provided
  - prefer `v_results` view for most questions
  - always include `LIMIT 50`
- Keep medical guidance cautious and phrased as “next steps to discuss with your veterinarian.”

> **Important:** In the live demo, you’ll want the assistant to avoid giving definitive medical diagnosis. Keep the advice at the level of *interpretation + next steps*, clearly framed as a demo.

---

## 7) Streamlit diagnostics viewer (in-app)

### Minimal viewer components
- A selector: `visit_id` (or pet name)  
- A few “prebaked” queries shown as tables:
  - Visit summary
  - Tests list
  - Abnormal results
  - Full results for a selected test (CBC vs Chem)

Example queries (for Cursor to implement):
- Visit summary:
  ```sql
  SELECT v.visit_id, v.visit_datetime, p.name AS pet_name, p.species, v.chief_complaint
  FROM visits v JOIN pets p ON p.pet_id = v.pet_id
  ORDER BY v.visit_datetime DESC
  LIMIT 20;
  ```
- Abnormal results for a visit:
  ```sql
  SELECT analyte_code, analyte_name, value_num, unit, flag, test_name
  FROM v_results
  WHERE visit_id = ?
    AND flag IN ('H','L')
  ORDER BY test_name, analyte_code
  LIMIT 50;
  ```

---

## 8) External SQLite viewer options (optional)

If you prefer to “peek under the hood” outside Streamlit:

### Option A: DB Browser for SQLite (GUI)
- Easy, popular, cross-platform
- Open the `.db` file and browse tables/views

### Option B: Datasette (local web UI)
- `pip install datasette`
- Run: `datasette diagnostics/diagnostics.db`
- Opens a local web app to browse tables and run queries

Recommendation: **use the in-app viewer** first (fewer moving parts), keep Datasette as a nice “bonus” for curious developers.

---

## 9) File/folder changes to implement

### New files (recommended)
- `diagnostics/`
  - `schema.sql`
  - `db.py` (create/open db, run migrations)
  - `seed.py` (insert demo data)
  - `queries.py` (helpers for viewer queries)
- `agentic/`
  - `agentic.py` (orchestrator)
  - `tools.py` (search_transcripts, query_diagnostics)
  - `sql_safety.py` (simple SQL allowlist)
- `sample_docs/`
  - add `visit_transcript_daisy.md` (we’ll fabricate later)
  - optionally `discharge_instructions.md`

### Modified files
- `app.py`
  - add mode selector
  - route chat calls to:
    - model-only handler
    - classic RAG handler
    - agentic handler
  - add “How I answered” trace UI
  - add diagnostics viewer section
- `requirements.txt`
  - likely add: `pandas` (for tables), maybe `sqlparse` (optional), `datasette` (optional)

---

## 10) Implementation notes & guardrails

### SQL safety (important even for demos)
In `query_diagnostics`:
- Reject anything not starting with `SELECT` (case-insensitive, whitespace-tolerant)
- Reject semicolons `;` (or split and allow only one statement)
- Reject keywords: `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `ATTACH`, `DETACH`, `PRAGMA`, `VACUUM`
- Enforce `LIMIT` (append if missing)

### Agent loop safety
- Hard cap tool calls: 3
- Hard cap retrieved chunks: top_k 4–6
- Hard cap SQL rows returned: 50
- If missing evidence: ask a clarifying question or say what it cannot find

### Medical safety (tone)
- The assistant should avoid definitive diagnosis.
- Use language like:
  - “These results can be consistent with…”
  - “Discuss with your veterinarian…”
  - “If symptoms worsen, seek veterinary attention…”

---

## 11) “Hero questions” to validate the three levels (for later)

We’ll create these after wiring is done, but design for questions like:

1) **No RAG**
- “My dog is vomiting and lethargic. What could it be?”

2) **Classic RAG**
- “What did the vet recommend we do at home after the visit?”
- “Summarize the visit and draft SOAP notes.”

3) **Agentic Context**
- “Which lab values were abnormal and what might they indicate?”
- “Do the lab results support dehydration? Show me the evidence.”
- “What follow-up tests did the vet mention, and do the lab results suggest urgency?”

---

## 12) Acceptance checklist (what “done” looks like)

- [ ] Mode selector works: three modes
- [ ] Classic RAG still works exactly as before for transcript docs
- [ ] SQLite DB created automatically if missing
- [ ] Seed data can be loaded with one button (or CLI)
- [ ] Agentic mode:
  - [ ] can search transcript and query SQL
  - [ ] shows trace: tools used, citations, SQL snippet
  - [ ] answers are grounded + have confidence level
- [ ] Diagnostics viewer shows the same results the agent is using

---

## 13) Next step after this design doc

1) Create a new branch and implement the scaffolding (schema + DB wiring + UI mode selector + agentic tool plumbing).  
2) Once the plumbing is working, we’ll fabricate:
   - the visit transcript markdown doc(s)
   - the diagnostic seed data rows aligned to the transcript narrative  
3) After you validate the demo works, we’ll build:
   - presentation outline
   - 2–3 slides that explain “context maturity”
   - live demo script + talking points

---

## Appendix A — Suggested environment/config variables

- `OPENAI_API_KEY` (existing)
- `RAG_STORE_PATH` (existing)
- `DIAGNOSTICS_DB_PATH=diagnostics/diagnostics.db`
- `AGENT_MAX_TOOL_CALLS=3`
- `SQL_MAX_ROWS=50`

---

## Appendix B — If you want an “even more agentic” but still simple extension

After the base is working, add one lightweight “clarifier tool”:

- `get_recent_visits(pet_name: str) -> list`
  - Returns the most recent visits for a pet (from SQLite)
  - Lets the agent ask: “Do you mean the visit on Jan 5 or Jan 10?”

This makes the agent feel smarter without adding new infrastructure.
