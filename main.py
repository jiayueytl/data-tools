import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="JSONL Viewer", layout="wide")
st.title("📄 JSONL Viewer (Single Entry Navigation)")

# --- 1. Upload JSONL file ---
uploaded_file = st.file_uploader("Upload a .jsonl file", type=["jsonl"])

if uploaded_file is not None:
    st.success("File uploaded successfully!")

    # --- 2. Parse JSONL ---
    data_list = []
    for line in uploaded_file:
        try:
            obj = json.loads(line.decode('utf-8'))
            data_list.append(obj)
        except Exception as e:
            st.error(f"Error parsing line: {e}")

    st.info(f"Total entries loaded: {len(data_list)}")

    if data_list:
        # --- Navigation State ---
        if "index" not in st.session_state:
            st.session_state.index = 0  # start from first entry

        col1, col2, col3 = st.columns([1,2,1])
        with col1:
            if st.button("⬅️ Previous") and st.session_state.index > 0:
                st.session_state.index -= 1
        with col3:
            if st.button("Next ➡️") and st.session_state.index < len(data_list) - 1:
                st.session_state.index += 1

        # Dropdown to jump directly
        options = [f"Entry {i} | ID: {entry.get('id','N/A')}" for i, entry in enumerate(data_list)]
        selected_option = st.selectbox(
            "Jump to entry",
            options,
            index=st.session_state.index
        )
        st.session_state.index = int(selected_option.split(" ")[1])
        entry = data_list[st.session_state.index]

        st.markdown("---")
        st.subheader(f"Entry {st.session_state.index} | ID: {entry.get('id','N/A')}")

        # Tags
        st.markdown(f"**Tag1:** {entry.get('tag1','')}")
        st.markdown(f"**Tag2:** {entry.get('tag2','')}")

        # Messages or prompt
        if "messages" in entry:
            messages = entry.get("messages", {}).get("Messages", [])
            if messages:
                st.markdown("**Messages:**")
                for msg in messages:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    st.markdown(f"- **{role}:** {content}")

            reasoning = entry.get("messages", {}).get("Reasoning", "")
            if reasoning:
                st.markdown("**Reasoning / Analysis:**")
                st.markdown(reasoning)

        elif "prompt" in entry:
            prompts = entry.get("prompt", [])
            if prompts:
                st.markdown("**Prompts:**")
                for i, p in enumerate(prompts):
                    role = p.get("role", "")
                    content = p.get("content", "")
                    st.markdown(f"- **{role}:** {content}")

        # Raw JSON
        with st.expander("Raw JSON"):
            st.code(json.dumps(entry, ensure_ascii=False, indent=2))

else:
    st.info("Upload a JSONL file to start viewing entries.")
