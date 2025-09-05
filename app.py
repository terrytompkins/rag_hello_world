
import os
import streamlit as st
from openai import OpenAI
from rag_utils import add_document_to_store, search, load_store, clear_store

st.set_page_config(page_title="RAG Hello World", page_icon="📚", layout="wide")
st.title("📚 RAG Hello World — Streamlit + OpenAI")
st.caption("Upload markdown docs, ask questions, and compare model-only vs RAG-grounded answers.")

if "OPENAI_API_KEY" not in os.environ:
    st.warning("Set the OPENAI_API_KEY environment variable before running. e.g., export OPENAI_API_KEY=sk-...")
client = OpenAI()

with st.sidebar:
    st.header("Settings")
    use_rag = st.toggle("Use RAG retrieval", value=False, help="Turn off to show model-only; turn on to ground with retrieved chunks.")
    top_k = st.slider("Top-k chunks", 1, 8, 4)
    model = st.text_input("Chat model", value=os.environ.get("CHAT_MODEL", "gpt-4o-mini"))
    st.divider()
    st.subheader("Document store")
    store_path = os.environ.get("RAG_STORE_PATH", "rag_store.json")
    store = load_store(store_path)
    st.write(f"Chunks indexed: **{len(store['chunks'])}**")
    if st.button("Clear document store"):
        clear_store(store_path)
        st.success("Cleared document store.")
    st.subheader("Add documents")
    files = st.file_uploader("Drop markdown (.md) files", type=["md","markdown","txt"], accept_multiple_files=True)
    if files:
        total = 0
        for f in files:
            content = f.read().decode("utf-8", errors="ignore")
            total += add_document_to_store(f.name, content, store_path=store_path)
        st.success(f"Indexed {total} chunks from {len(files)} file(s).")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask a question about your docs (or anything)")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    context_blocks, citations = [], []
    if use_rag:
        hits = search(prompt, k=top_k, store_path=store_path)
        if hits:
            for idx, h in enumerate(hits, start=1):
                context_blocks.append(f"[{idx}] source: {h['source']}\n{h['text']}")
                citations.append(f"[{idx}] {h['source']} (score {h['score']:.3f})")
        else:
            citations.append("_No documents in store or no matches._")

    system_prompt = (
        "You are a concise, helpful assistant.\n"
        "If RAG context is provided, ground your answer primarily in that context and reference sources like [1], [2].\n"
        "If the context is irrelevant or insufficient, say so explicitly before answering from general knowledge.\n"
    )

    messages = [{"role":"system","content":system_prompt}]
    if use_rag and context_blocks:
        messages.append({"role":"user","content":"RAG context:\n" + "\n\n".join(context_blocks)})
    history_tail = st.session_state.messages[-4:]
    for m in history_tail:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role":"user","content":prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            client = OpenAI()
            resp = client.chat.completions.create(model=model, messages=messages, temperature=0.2)
            answer = resp.choices[0].message.content
            st.markdown(answer)
            if use_rag:
                with st.expander("Show retrieved sources"):
                    st.markdown("\n".join(f"- {c}" for c in citations))
    st.session_state.messages.append({"role":"assistant","content":answer})
