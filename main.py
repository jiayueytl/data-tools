import streamlit as st
import json
import pandas as pd

st.set_page_config(page_title="DNA Data Tools", layout="wide")

# --- Page Navigation ---
page = st.sidebar.selectbox("Select Page", ["JSONL Viewer", "Comparison Viewer"])

# --- JSONL Viewer Page ---
if page == "JSONL Viewer":
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

            # Handle empty filtered results
            if not filtered:
                st.warning("No entries match your filter.")
                st.stop()

            # Navigation state
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
                f"Entry {i} | ID: {entry.get('original_id', entry.get('id', 'N/A'))}"
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
            st.subheader(f"Entry {st.session_state.index} | ID: {entry.get('original_id','N/A')}")

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

# --- Comparison Viewer Page ---
elif page == "Comparison Viewer":
    # st.set_page_config(page_title="JSON Comparison Viewer", layout="wide")
    st.title("🔍 JSON Comparison Viewer")

    # Upload JSON file (single entry or list)
    uploaded_file = st.file_uploader("Upload a JSON file or JSONL", type=["json", "jsonl"], key="comparison")

    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
        except Exception as e:
            st.error(f"Error loading JSON: {e}")
            st.stop()

        # If it's a list, let user pick an entry
        if isinstance(data, list):
            selected_index = st.number_input(
                "Select entry index",
                min_value=0,
                max_value=len(data) - 1,
                value=0,
                step=1
            )
            entry = data[selected_index]
        elif isinstance(data, dict):
            entry = data
        else:
            st.error("Unsupported JSON structure")
            st.stop()

        # --- Extract messages and revised ---
        messages_data = entry.get("messages", {})
        revised = entry.get("revised_messages", {})

        chat_messages = messages_data.get("Messages", [])
        reasoning = messages_data.get("Reasoning", "No reasoning found")

        # Revised content
        revised_content_list = revised.get("revised_response", [])
        if revised_content_list:
            first_item = revised_content_list[0]
            if isinstance(first_item, dict):
                revised_content = first_item.get("content", "No revised content")
            elif isinstance(first_item, str):
                revised_content = first_item
        else:
            revised_content = "No revised content"

        # Revised reasoning
        revised_reasoning = revised.get("revised_reasoning", "No revised reasoning")
        if revised_reasoning in ["", "N/A", None]:
            revised_reasoning = "No revised reasoning"

        # --- Top: Chat history ---
        st.subheader("💬 Chat History")
        if chat_messages:
            for msg in chat_messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role.lower() == "user":
                    st.markdown(f"<div style='background-color:#f0f8ff; padding:8px; border-radius:5px;'><b>User:</b> {content}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='background-color:#e6ffe6; padding:8px; border-radius:5px;'><b>Assistant:</b> {content}</div>", unsafe_allow_html=True)
        else:
            st.info("No chat messages found.")

        st.markdown("---")

        # --- Bottom: Content and Reasoning Comparison ---
        st.subheader("📝 Original vs Revised")

        def wrap_text(text):
            return f"<div style='white-space: pre-wrap; word-wrap: break-word; padding:8px; border:1px solid #ddd; border-radius:5px; background-color:#f9f9f9'>{text}</div>"

        # Row 1: Original content | Original reasoning
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.markdown("**Original Content**")
            last_user_assistant = chat_messages[-1] if chat_messages else {}
            last_content = last_user_assistant.get("content", "No content found")
            st.markdown(wrap_text(last_content), unsafe_allow_html=True)

        st.markdown("---")
        with row1_col2:
            st.markdown("**Revised Content**")
            st.markdown(wrap_text(revised_content), unsafe_allow_html=True)

        # Row 2: Revised content | Revised reasoning
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.markdown("**Original Reasoning**")
            st.markdown(wrap_text(reasoning), unsafe_allow_html=True)

        with row2_col2:
            st.markdown("**Revised Reasoning**")
            st.markdown(wrap_text(revised_reasoning), unsafe_allow_html=True)

