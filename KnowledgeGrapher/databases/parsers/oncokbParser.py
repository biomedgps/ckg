import os.path
from KnowledgeGrapher.databases import databases_config as dbconfig
from KnowledgeGrapher.databases.config import oncokbConfig as iconfig
from KnowledgeGrapher import mapping as mp
from collections import defaultdict
from KnowledgeGrapher import utils
import re
#########################
#   OncoKB database     #
#########################
def parser(download = False):
    url_actionable = iconfig.OncoKB_actionable_url
    url_annotated = iconfig.OncoKB_annotated_url
    entities_header = iconfig.entities_header
    relationships_headers = iconfig.relationships_headers
    mapping = mp.getMappingFromOntology(ontology = "Disease", source = None)

    drugsource = dbconfig.sources["Drug"]
    directory = os.path.join(dbconfig.databasesDir, drugsource)
    mappingFile = os.path.join(directory, "mapping.tsv")
    drugmapping = mp.getMappingFromDatabase(mappingFile)

    levels = iconfig.OncoKB_levels
    entities = set()
    relationships = defaultdict(set)
    directory = os.path.join(dbconfig.databasesDir,"OncoKB")
    utils.checkDirectory(directory)
    acfileName = os.path.join(directory,url_actionable.split('/')[-1])
    anfileName = os.path.join(directory,url_annotated.split('/')[-1])
    if download:
        utils.downloadDB(url_actionable, "OncoKB")
        utils.downloadDB(url_annotation, "OncoKB")

    regex = r"\w\d+(\w|\*|\.)"
    with open(anfileName, 'r') as variants:
        first = True
        for line in variants:
            if first:
                first = False
                continue
            data = line.rstrip("\r\n").split("\t")
            gene = data[3]
            variant = data[4]
            oncogenicity = data[5]
            effect = data[6]          
            entities.add((variant,"Clinically_relevant_variant", "", "", "", "", "", effect, oncogenicity))
            relationships["variant_found_in_gene"].add((variant, gene, "VARIANT_FOUND_IN_GENE"))

    with open(acfileName, 'r') as associations:
        first = True
        for line in associations:
            if first:
                first = False
                continue
            data = line.rstrip("\r\n").split("\t")
            isoform = data[1]
            gene = data[3]
            variant = data[4]
            disease = data[5]
            level = data[6]
            drugs = data[7].split(', ')
            pubmed_ids = data[8].split(',')
            if level in levels:
                level = levels[level]
            for drug in drugs:
                if drug.lower() in drugmapping:
                    drug = drugmapping[drug.lower()]
                else:
                    pass
                    #print drug
                if disease.lower() in mapping:
                    disease = mapping[disease.lower()]
                else:
                    pass
                    #print disease
                relationships["targets_clinically_relevant_variant"].add((drug, variant, "TARGETS_KNOWN_VARIANT", level[0], level[1], disease, "curated", "OncoKB"))
                relationships["associated_with"].add((variant, disease, "ASSOCIATED_WITH", "curated","curated", "OncoKB", len(pubmed_ids)))   
                relationships["targets"].add((drug, gene, "CURATED_TARGETS", "curated", "OncoKB"))
                relationships["known_variant_is_clinically_relevant"].add((variant, variant, "KNOWN_VARIANT_IS_CLINICALLY_RELEVANT", "OncoKB"))
        relationships["variant_found_in_chromosome"].add(("","",""))


    return (entities, relationships, entities_header, relationships_headers)