import glob
import json
import os

ALL_TRIPLES_SPARQL = "SELECT * WHERE { ?s ?p ?o. } LIMIT 25"
# TODO provide some registry of endpoints to choose from --> issue #4
#   then replace next line!
BODC_ENDPOINT = "http://vocab.nerc.ac.uk/sparql/sparql"

FILES_SOURCE = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "sources"
)
TTL_FILES_TO_TEST = glob.glob(f"{FILES_SOURCE}/*.ttl")

QUERY_RESULT_PATH = f"{FILES_SOURCE}/query_result.json"
with open(QUERY_RESULT_PATH) as src:
    TTL_FILES_QUERY_RESULT = json.load(src)

TTL_FILE_IN_URI = (
    "https://raw.githubusercontent.com/"
    "ukgovld/registry-core/master/src/main/vocabs/registryVocab.ttl"
)
