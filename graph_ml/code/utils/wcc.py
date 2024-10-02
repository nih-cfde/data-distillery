


def weakly_connected_components(gds,G):
    '''
    Run WCC on the graph. It will assign an ID to nodes that are connected together.
    Then we extract the largest connected subgraph by its id, and then lastly remove the 
    wcc property and return this new fully connected subgraph.
    
    https://neo4j.com/docs/graph-data-science-client/current/tutorials/community-detection/#_weakly_connected_components

    WCC can help identify discrete unconnected graphs. Below is an example of how to get the number and size of 
    each disconnected graphs, and also how to project one of the seperate graphs as a subgraph.
    '''
    
    # if we just want to mutate a component ID onto the projected graph, just run this.
    wcc_result = gds.wcc.mutate(G, mutateProperty="wccComponentId")
    
    assert 'wccComponentId' in G.node_properties()[0]
    print(f"Components found: {wcc_result.componentCount}")
    
    # Get additional information, instead of just mutating property
    wcc_query = f"""
        CALL gds.graph.nodeProperties.stream('{G.name()}', 'wccComponentId')
        YIELD nodeId, propertyValue
        WITH nodeId AS node, propertyValue AS componentId// gds.util.asNode(nodeId).name AS node, propertyValue AS componentId
        WITH componentId, collect(node) AS comps
        WITH componentId, comps, size(comps) AS componentSize
        RETURN componentId, componentSize, comps ORDER BY componentSize DESC"""
    
    components = gds.run_cypher(wcc_query)
    largest_component = components["componentId"][0]
    
    print(f"The largest component has the id {largest_component} with {components['componentSize'][0]} nodes.")
    
    # For our further analysis we will work only with that subgraph.
    largest_component_graph, _ = gds.beta.graph.project.subgraph(
        "largest_connected_components", G, f"n.wccComponentId={largest_component}", "*")
    
    W = largest_component_graph # set new graph to W
    
    # Remove wccComponentId property
    q=f"""CALL gds.graph.nodeProperties.drop('{W.name()}', ['wccComponentId']) YIELD propertiesRemoved"""
    
    gds.run_cypher(q)
    
    # check that this largest component really has no disconnected nodes
    wcc_result = gds.wcc.stream(W)
    assert len(wcc_result['componentId'].unique()) == 1
    
    return W


