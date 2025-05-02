from langchain_community.llms import Ollama
import requests
import re

# Configure LLM and Fuseki endpoint
llm = Ollama(model="llama3")
FUSEKI_ENDPOINT = "http://localhost:3030/amzn/sparql"

# Prompt template
prompt = """
You are a SPARQL expert.
Given a question about financial facts from an RDF graph using this structure:

@prefix ex: <http://example.org/amzn/> .
ex:AccountsPayableCurrent ex:value 84981.0 .

Generate a SPARQL query that retrieves values directly from triples like:
ex:<concept> ex:value ?value .

Question: {question}

SPARQL:
"""

def extract_sparql(text):
    match = re.search(r"(?i)select\s.*?\{.*?\}", text, re.DOTALL)
    if match:
        return f"PREFIX ex: <http://example.org/amzn/>\n\n{match.group(0).strip()}"
    return None

def ask_question(question):
    print(f"\n🧠 Asking LLM:\n{prompt.format(question=question)}")
    llm_output = llm.invoke(prompt.format(question=question))
    
    print(f"\n🧠 Generated SPARQL Query:\n{llm_output}")
    sparql_query = extract_sparql(llm_output)

    if not sparql_query:
        print("❌ Failed to extract SPARQL from model response.")
        return

    headers = {'Content-Type': 'application/sparql-query'}
    response = requests.post(FUSEKI_ENDPOINT, data=sparql_query, headers=headers)

    if response.status_code == 200:
        print("\n✅ Query Result:")
        print(response.text)
    else:
        print(f"\n❌ SPARQL failed: {response.text}")
        print(f"Status Code: {response.status_code}")

if __name__ == "__main__":
    q = input("Ask about AMZN data: ")
    ask_question(q)
