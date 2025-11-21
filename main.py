import streamlit as st
import json

st.set_page_config(page_title="DNA Data Tools", layout="wide")

# ------------------------
# Helper Functions
# ------------------------

def load_json_or_jsonl(uploaded_file):
    """Load JSON or JSONL file and return list or dict"""
    try:
        data = json.load(uploaded_file)
        return data
    except Exception:
        # Try line by line as JSONL
        uploaded_file.seek(0)
        data_list = []
        for line in uploaded_file:
            try:
                obj = json.loads(line.decode("utf-8"))
                data_list.append(obj)
            except Exception as e:
                st.error(f"Error parsing line: {e}")
        return data_list

def wrap_text(text):
    """Wrap text for Streamlit markdown"""
    return f"<div style='white-space: pre-wrap; word-wrap: break-word; padding:8px; border:1px solid #ddd; border-radius:5px; background-color:#f9f9f9'>{text}</div>"

def render_chat_history(chat_messages):
    """Render user-assistant chat pairs"""
    st.subheader("💬 Chat History")
    if chat_messages:
        for msg in chat_messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            color = "#f0f8ff" if role.lower() == "user" else "#e6ffe6"
            st.markdown(f"<div style='background-color:{color}; padding:8px; border-radius:5px; margin-bottom:4px'><b>{role.title()}:</b> {content}</div>", unsafe_allow_html=True)
    else:
        st.info("No chat messages found.")

def render_comparison(chat_messages, reasoning, revised_content, revised_reasoning):
    """Render bottom comparison in 2x2 layout with text wrapping"""
    st.subheader("📝 Original vs Revised")
    
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.markdown("**Original Content**")
        last_content = chat_messages[-1].get("content", "No content found") if chat_messages else "No content found"
        st.markdown(wrap_text(last_content), unsafe_allow_html=True)

    with row1_col2:
        st.markdown("**Revised Content**")
        st.markdown(wrap_text(revised_content), unsafe_allow_html=True)

    st.markdown("---")
    
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.markdown("**Original Reasoning**")
        st.markdown(wrap_text(reasoning), unsafe_allow_html=True)

    with row2_col2:
        st.markdown("**Revised Reasoning**")
        st.markdown(wrap_text(revised_reasoning), unsafe_allow_html=True)

def navigate_entries(filtered, index_key="index", prefix="nav"):
    """Create <- and -> navigation buttons with unique keys"""
    if index_key not in st.session_state:
        st.session_state[index_key] = 0

    col_prev, col_index, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("⬅️ Previous", key=f"{prefix}_prev"):
            if st.session_state[index_key] > 0:
                st.session_state[index_key] -= 1
    with col_index:
        st.markdown(f"**Entry {st.session_state[index_key]+1} / {len(filtered)}**", unsafe_allow_html=True)
    with col_next:
        if st.button("Next ➡️", key=f"{prefix}_next"):
            if st.session_state[index_key] < len(filtered) - 1:
                st.session_state[index_key] += 1

    return st.session_state[index_key]

# ------------------------
# JSONL Viewer Page
# ------------------------
def jsonl_viewer():
    st.title("📄 JSONL Viewer")
    uploaded_file = st.file_uploader("Upload a .jsonl file", type=["jsonl"], key="jsonl_viewer")
    if uploaded_file is None:
        st.info("Upload a JSONL file to start viewing entries.")
        return

    data_list = load_json_or_jsonl(uploaded_file)
    if not data_list:
        st.warning("No entries loaded from file.")
        return

    # Filter by tags
    all_tag1 = sorted({d.get("tag1") for d in data_list if "tag1" in d})
    all_tag2 = sorted({d.get("tag2") for d in data_list if "tag2" in d})
    col1, col2 = st.columns(2)
    with col1:
        selected_tag1 = st.selectbox("Filter Tag1", ["All"] + all_tag1 if all_tag1 else ["No tag1 in file"])
    with col2:
        selected_tag2 = st.selectbox("Filter Tag2", ["All"] + all_tag2 if all_tag2 else ["No tag2 in file"])

    filtered = data_list
    if selected_tag1 != "All":
        filtered = [d for d in filtered if d.get("tag1") == selected_tag1]
    if selected_tag2 != "All":
        filtered = [d for d in filtered if d.get("tag2") == selected_tag2]

    if not filtered:
        st.warning("No entries match your filter.")
        return

    # --- Top Navigation ---
    current_index = navigate_entries(filtered, index_key="jsonl_index", prefix="jsonl_top")

    entry = filtered[current_index]

    st.markdown(f"**ID:** {entry.get('original_id', entry.get('id','N/A'))}")
    st.markdown(f"**Tag1:** {entry.get('tag1','')}")
    st.markdown(f"**Tag2:** {entry.get('tag2','')}")

    # Messages / Prompts
    if "messages" in entry:
        messages = entry.get("messages", {}).get("Messages", [])
        reasoning = entry.get("messages", {}).get("Reasoning", "")
    elif "prompt" in entry:
        messages = entry.get("prompt", [])
        reasoning = ""
    else:
        messages = []
        reasoning = ""

    if messages:
        render_chat_history(messages)
    if reasoning:
        st.markdown("**Reasoning / Analysis:**")
        st.markdown(wrap_text(reasoning), unsafe_allow_html=True)

    # Raw JSON
    with st.expander("Raw JSON"):
        st.code(json.dumps(entry, ensure_ascii=False, indent=2))

    # --- Bottom Navigation ---
    st.markdown("---")
    navigate_entries(filtered, index_key="jsonl_index", prefix="jsonl_bottom")

# ------------------------
# Comparison Viewer Page
# ------------------------
def comparison_viewer():
    st.title("🔍 JSON Comparison Viewer")
    uploaded_file = st.file_uploader("Upload a JSON file or JSONL", type=["json","jsonl"], key="comparison_viewer")
    if uploaded_file is None:
        st.info("Upload a JSON/JSONL file to view comparison.")
        return

    data = load_json_or_jsonl(uploaded_file)
    data_list = data if isinstance(data, list) else [data]

    # --- Top Navigation ---
    current_index = navigate_entries(data_list, index_key="comparison_index", prefix="comp_top")
    entry = data_list[current_index]

    messages_data = entry.get("messages", {})
    revised = entry.get("revised_messages", {})

    st.markdown(f"**ID:** {entry.get('original_id', entry.get('id','N/A'))}")
    st.markdown(f"**Tag1:** {entry.get('tag1','')}")
    st.markdown(f"**Tag2:** {entry.get('tag2','')}")

    chat_messages = messages_data.get("Messages", [])
    reasoning = messages_data.get("Reasoning", "No reasoning found")

    # Revised content
    revised_content_list = revised.get("revised_response", [])
    if revised_content_list:
        first_item = revised_content_list[0]
        revised_content = first_item.get("content") if isinstance(first_item, dict) else first_item
    else:
        revised_content = "No revised content"

    # Revised reasoning
    revised_reasoning = revised.get("revised_reasoning", "No revised reasoning")
    if revised_reasoning in ["", "N/A", None]:
        revised_reasoning = "No revised reasoning"

    # Render
    st.write()
    render_chat_history(chat_messages)
    render_comparison(chat_messages, reasoning, revised_content, revised_reasoning)

    # --- Bottom Navigation ---
    st.markdown("---")
    navigate_entries(data_list, index_key="comparison_index", prefix="comp_bottom")

# ------------------------
# Main Navigation
# ------------------------
page = st.sidebar.selectbox("Select Page", ["JSONL Viewer", "Comparison Viewer"])
if page == "JSONL Viewer":
    jsonl_viewer()
elif page == "Comparison Viewer":
    comparison_viewer()
