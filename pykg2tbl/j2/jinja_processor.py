#TODO take over py-vocab-search from gitlab

# will be the jinja based sparql query builder
class JinjaBasedSparqlQueryBuilder():
    def __init__(self, templateFolder:str) -> None:
        self.jinjaContext = templateFolder #find instance variables in py-vocab-search

    def get_sparql(self, name:str, **params):
        #TODO Build template from name 
        #TODO execute template with passed down params
        pass