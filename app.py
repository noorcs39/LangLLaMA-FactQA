import streamlit as st
from langchain_community.llms import Ollama
import requests
import re

FUSEKI_ENDPOINT = "http://localhost:3030/amzn/sparql"

st.set_page_config(page_title="Chatbot", page_icon="📊")
st.title("📊 Financial Fact Extraction from Amazon 10-K Using RDF, SPARQL, LangChain, and LLaMA 3")
st.write("Ask a financial question about Amazon's 10-K:")

question = st.text_input("", "What is the value of AccountsPayableCurrent?")

if st.button("Submit"):
    with st.spinner("🧠 Asking LLM..."):
        prompt = '''
You are a SPARQL expert.
Given a question about financial facts from an RDF graph using this structure:

@prefix ex: <http://example.org/amzn/> .
ex:AccountsPayableCurrent ex:value 84981.0 .

Generate a SPARQL query that retrieves values directly from triples like:
ex:<concept> ex:value ?value .

Question: {question}

SPARQL:
'''

        llm = Ollama(model="llama3")
        query_prompt = prompt.format(question=question)
        llm_output = llm.invoke(query_prompt)

        st.subheader("🧠 LLM Output")
        st.code(llm_output)

        def extract_sparql(text):
            match = re.search(r"```sparql\s+(.*?)```", text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
            match = re.search(r"SELECT\s+.*?\{.*?\}", text, re.DOTALL | re.IGNORECASE)
            if match:
                return f"PREFIX ex: <http://example.org/amzn/>\n\n{match.group(0).strip()}"
            return None

        sparql_query = extract_sparql(llm_output)

        if sparql_query:
            st.subheader("📥 SPARQL Query")
            st.code(sparql_query, language="sparql")

            headers = {
                "Accept": "application/sparql-results+json",
                "Content-Type": "application/sparql-query"
            }
            try:
                response = requests.post(FUSEKI_ENDPOINT, headers=headers, data=sparql_query.encode("utf-8"))
                result = response.json()
                bindings = result.get("results", {}).get("bindings", [])

                if bindings:
                    st.success("✅ Answer:")
                    for row in bindings:
                        st.write("•", row['value']['value'])
                else:
                    st.warning("No results returned from the SPARQL query.")
            except Exception as e:
                st.error(f"❌ SPARQL failed: {e}")
        else:
            st.error("Failed to extract SPARQL query from LLM output.")