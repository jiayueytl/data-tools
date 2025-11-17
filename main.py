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

        # ----------------------------------------------------
        # 🔍 TAG FILTERS
        # ----------------------------------------------------
        all_tag1 = sorted(list({d.get("tag1") for d in data_list if "tag1" in d}))
        all_tag2 = sorted(list({d.get("tag2") for d in data_list if "tag2" in d}))

        colf1, colf2 = st.columns(2)

        with colf1:
            selected_tag1 = st.selectbox(
                "Filter Tag1",
                ["All"] + all_tag1 if all_tag1 else ["No tag1 in file"]
            )

        with colf2:
            selected_tag2 = st.selectbox(
                "Filter Tag2",
                ["All"] + all_tag2 if all_tag2 else ["No tag2 in file"]
            )

        # Apply filter
        filtered = data_list
        if selected_tag1 != "All" and "No tag1" not in selected_tag1:
            filtered = [d for d in filtered if d.get("tag1") == selected_tag1]

        if selected_tag2 != "All" and "No tag2" not in selected_tag2:
            filtered = [d for d in filtered if d.get("tag2") == selected_tag2]

        # ----------------------------------------------------
        # Handle empty filtered results
        # ----------------------------------------------------
        if not filtered:
            st.warning("No entries match your filter.")
            st.stop()

        # ----------------------------------------------------
        # Navigation state
        # ----------------------------------------------------
        if "index" not in st.session_state:
            st.session_state.index = 0

        # Fix index overflow after filtering
        if st.session_state.index >= len(filtered):
            st.session_state.index = 0

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Previous") and st.session_state.index > 0:
                st.session_state.index -= 1
        with col3:
            if st.button("Next ➡️") and st.session_state.index < len(filtered) - 1:
                st.session_state.index += 1

        # Jump dropdown
        options = [
            f"Entry {i} | ID: {entry.get('id', 'N/A')}"
            for i, entry in enumerate(filtered)
        ]
        selected_option = st.selectbox(
            "Jump to entry",
            options,
            index=st.session_state.index
        )
        st.session_state.index = int(selected_option.split(" ")[1])
        entry = filtered[st.session_state.index]

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
