

def make_llm_subgraph(gds):
    '''
    the LLM subgraph projection does NOT need to include properties on the nodes, 
    bc we need to export it, and theres an option to add the properties to the 
    exported graph when using the export function...so we can leave out the 
    sourceNodeProperties and targetNodeProperties args from the projection here.
    
    ex of args we removed:
    sourceNodeProperties: source {{ SAB_CAT: coalesce(source.SAB_CAT, -1)}},   
    targetNodeProperties: target {{ SAB_CAT: coalesce(target.SAB_CAT, -1)}}
    '''
    
    # 'CL', 'FMA','NCI','SNOMEDCT_US','MONDO','GO','OMIM','PATO','DSM-5','ICD10','ORPHANET','MP'
    sabs=['HGNC','HP','UBERON', 'DOID']
    GRAPH_NAME='newG'
    #inverse_rel_exclude=['']   //AND inverse_rel_exclude AS INV_REL_EXLCUDE
    #labels_to_include='Concept|Gene|Phenotype|Tissue|Disease|CellType'     

    q=f"""WITH {sabs} as sabs 
    MATCH (source:Gene|Phenotype|Tissue|Disease)-[r1]->(target:Gene|Phenotype|Tissue|Disease) 
    WHERE source.SAB IN sabs AND target.SAB IN sabs AND NOT type(r1) CONTAINS 'coexp' 
    AND NOT type(r1) CONTAINS 'inverse' AND NOT type(r1) = 'HGNC_associated_with_HP' 
    WITH gds.graph.project('{GRAPH_NAME}',source,target,
      {{
        sourceNodeLabels: labels(source),
        targetNodeLabels: labels(target),
        relationshipType: type(r1)
      }},  {{  undirectedRelationshipTypes: ['*'] }} ) AS g        
    RETURN g.graphName AS graph, g.nodeCount AS nodes, g.relationshipCount AS rels"""
    
    result = gds.run_cypher(q)
    graph_obj = gds.graph.get(GRAPH_NAME)
    
    return result, graph_obj
    