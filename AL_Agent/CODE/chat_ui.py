import streamlit as st
import requests
import os

# ✅ Page settings
st.set_page_config(page_title="E-commerce AI Chatbot", page_icon="🛍️")
st.title("🛍️ E-commerce Data Chatbot")
st.caption("Ask anything about your product sales, ads, and trends!")

# ✅ Option to clear chat
if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = []

# ✅ Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ✅ Query form to prevent automatic re-runs
with st.form(key="query_form"):
    user_input = st.text_input("Enter your question:", placeholder="e.g., What is my total sales?")
    submitted = st.form_submit_button("Ask")

# ✅ Handle submission
if submitted and user_input.strip():
    st.session_state.chat_history.append(("You", user_input))

    with st.spinner("🧠 Thinking..."):
        try:
            is_graph = any(word in user_input.lower() for word in ["graph", "chart", "plot", "visualize", "trend"])
            endpoint = "graph" if is_graph else "query"
            url = f"http://127.0.0.1:8000/{endpoint}/?question={user_input}"

            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                print("✅ LLM Output:", data)

                if is_graph:
                    explanation = data.get("message", "Here's your graph ⬇️")
                    graph_path = data.get("graph_path", "graph.png")
                    st.session_state.chat_history.append(("AI_GRAPH", explanation, graph_path))
                else:
                    answer = data.get("answer", "No answer received.")
                    st.session_state.chat_history.append(("AI", answer))
            else:
                st.session_state.chat_history.append(("AI", f"⚠️ Error fetching response: {response.status_code}"))

        except requests.exceptions.RequestException:
            st.session_state.chat_history.append(("AI", "❌ Backend server is unreachable. Please check if FastAPI is running."))

# ✅ Display Chat History
for chat in st.session_state.chat_history:
    if chat[0] == "You":
        st.chat_message("user").markdown(f"🧑‍💼 **You:** {chat[1]}")
    elif chat[0] == "AI_GRAPH":
        _, explanation, graph_path = chat
        st.chat_message("assistant").markdown(f"📝 **Explanation:** {explanation}")
        if os.path.exists(graph_path):
            st.image(graph_path, caption="📊 Generated Graph", use_container_width=True)
        else:
            st.error("⚠️ Graph image not found. Please check server logs.")
    else:
        _, answer = chat
        st.chat_message("assistant").success(answer)
