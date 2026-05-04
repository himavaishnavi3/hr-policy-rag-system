import streamlit as st
from rag_pipeline import load_qa_chain

st.title("HR Policy RAG System")

# Load model
qa_chain = load_qa_chain()

# Input box
query = st.text_input("Ask your question:")

if st.button("Submit"):
    if query:
        result = qa_chain(query)

        st.subheader("Answer:")
        st.write(result["result"])

        st.subheader("Sources:")
        for doc in result["source_documents"]:
            st.write(doc.page_content)