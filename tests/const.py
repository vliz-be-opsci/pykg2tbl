import glob
import json
from pathlib import Path

from rdflib import Graph

graph = Graph()
ALL_TRIPLES_SPARQL = "SELECT * WHERE { ?s ?p ?o. } LIMIT 25"
# TODO provide some registry of endpoints to choose from --> issue #4
#   then replace next line!
BODC_ENDPOINT = "http://vocab.nerc.ac.uk/sparql/sparql"

ABS_PARENT_PATH = Path(__file__).parent.absolute()
SOURCES_PATH = ABS_PARENT_PATH / "sources"
TTL_FILES_TO_TEST = glob.glob(f"{ str(SOURCES_PATH) }/*.ttl")

for file in TTL_FILES_TO_TEST:
    graph.parse(file)

QUERY_RESULT_PATH = str(SOURCES_PATH / "query_result.json")
with open(QUERY_RESULT_PATH) as src:
    TTL_FILES_QUERY_RESULT = json.load(src)

TTL_FILE_IN_URI = (
    "https://raw.githubusercontent.com/"
    "ukgovld/registry-core/master/src/main/vocabs/registryVocab.ttl"
)

P06_DUMP_FILE = SOURCES_PATH / "bodc/20230605-P06-dump.ttl"
FAKE_DUMP_FILE = SOURCES_PATH / "bodc/fake-dump.ttl"
