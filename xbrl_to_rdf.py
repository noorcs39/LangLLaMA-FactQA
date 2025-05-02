from lxml import etree
from rdflib import Graph, URIRef, Literal, Namespace, RDF, XSD

# Load the iXBRL file
xbrl_file = "C:/Users/Noor/Downloads/Turing/amzn-20241231.htm"
tree = etree.parse(xbrl_file)
root = tree.getroot()

# Namespaces
EX = Namespace("http://example.org/amzn/")
USGAAP = Namespace("http://fasb.org/us-gaap/")
IX = "{http://www.xbrl.org/2013/inlineXBRL}"

g = Graph()
g.bind("ex", EX)
g.bind("us-gaap", USGAAP)

# Search for ix:nonFraction (iXBRL values)
for elem in root.iter():
    if "nonFraction" in elem.tag:
        concept = elem.get("name") or elem.get("contextRef")  # fallback
        if concept and concept.startswith("us-gaap"):
            tag = concept.split(":")[1]
            try:
                value = float(elem.text.strip().replace(",", ""))
            except:
                continue
            fact_uri = URIRef(EX[tag])
            g.add((fact_uri, RDF.type, URIRef(USGAAP[tag])))
            g.add((fact_uri, EX["value"], Literal(value, datatype=XSD.decimal)))

# Save RDF
g.serialize("amzn-2024.ttl", format="turtle")
print("✅ RDF saved with iXBRL facts")
