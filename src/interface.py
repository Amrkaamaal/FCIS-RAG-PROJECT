import os
from typing import Any, Dict, Optional

import requests
import streamlit as st


def request_json(
    method: str,
    base_url: str,
    path: str,
    **kwargs
) -> Optional[Dict[str, Any]]:

  url = f"{base_url.rstrip('/')}{path}"

  try:

    response = requests.request(method, url, timeout=30, **kwargs)

    response.raise_for_status()

  except requests.RequestException as exc:

    st.error(f"Request failed: {exc}")

    return None

  try:

    return response.json()

  except ValueError:

    st.warning("Response is not JSON")

    st.text(response.text)

    return None


st.set_page_config(page_title="Mini-RAG", layout="wide")

st.title("Mini-RAG Console")

base_url = st.sidebar.text_input(
    "API Base URL",
    os.getenv("API_BASE_URL", "http://localhost:8000")
)

st.sidebar.caption("Make sure the FastAPI service is running.")

with st.sidebar:

  if st.button("Check API"):

    info = request_json("GET", base_url, "/api/")

    if info:

      st.success("API reachable")

      st.json(info)


st.header("Upload Documents")

uploaded = st.file_uploader("Select a PDF or TXT file")

if st.button("Upload"):

  if not uploaded:

    st.warning("Please choose a file first.")

  else:

    files = {
        "file": (
            uploaded.name,
            uploaded.getvalue(),
            uploaded.type or "application/octet-stream"
        )
    }

    result = request_json("POST", base_url, "/api/data/upload", files=files)

    if result:

      st.json(result)


st.header("Process Files")

with st.form("process-form"):

  chunk_size = st.number_input("Chunk size", min_value=50, max_value=2000, value=200)

  overlap = st.number_input("Overlap", min_value=0, max_value=500, value=20)

  do_reset = st.checkbox("Reset existing chunks", value=False)

  submitted = st.form_submit_button("Process")

if submitted:

  payload = {
      "chunk_size": int(chunk_size),
      "overlap": int(overlap),
      "do_reset": bool(do_reset)
  }

  result = request_json("POST", base_url, "/api/data/process", json=payload)

  if result:

    st.json(result)


st.header("Indexing")

if st.button("Push Index"):

  payload = {"do_reset": False}

  result = request_json("POST", base_url, "/api/nlp/index/push", json=payload)

  if result:

    st.json(result)

if st.button("Reset + Push Index"):

  payload = {"do_reset": True}

  result = request_json("POST", base_url, "/api/nlp/index/push", json=payload)

  if result:

    st.json(result)


st.header("Search and Answer")

question = st.text_area("Ask a question", height=120)

top_k = st.number_input("Top K", min_value=1, max_value=50, value=5)

locale = st.selectbox("Locale", ["en", "ar"])

col_search, col_answer = st.columns(2)

with col_search:

  if st.button("Search"):

    payload = {"text": question, "top_k": int(top_k)}

    result = request_json("POST", base_url, "/api/nlp/search", json=payload)

    if result:

      st.json(result)

with col_answer:

  if st.button("Answer"):

    payload = {"text": question, "top_k": int(top_k)}

    result = request_json(
        "POST",
        base_url,
        "/api/nlp/answer",
        params={"locale": locale},
        json=payload
    )

    if result:

      st.json(result)


st.header("Service Info")

if st.button("Refresh Info"):

  info = request_json("GET", base_url, "/api/nlp/info")

  if info:

    st.json(info)
