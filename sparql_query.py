from rdflib import Graph

g = Graph()
g.parse("amzn-2024.ttl", format="turtle")

qres = g.query("""
PREFIX ex: <http://example.org/amzn/>
PREFIX us-gaap: <http://fasb.org/us-gaap/>

SELECT ?fact ?value WHERE {
  ?fact a ?type .
  ?fact ex:value ?value .
}
LIMIT 10
""")

print("🔎 Financial Facts:")
for row in qres:
    print(f"{row.fact.split('/')[-1]}: {row.value}")
