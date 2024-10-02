

import graphdatascience as gds


# add support for regular centrality props

def get_embeddings_and_plot(graph_obj,embedding_method, plot_by):
    '''Helper function to get the embedding vectors , do PCA and plot them in 2-D to see how well they seperate the nodes. Also
    will print how many unique vectors there are. '''
    
    # query node properties and return (embedding_method,SAB_CAT)
    query_get_props=f"""CALL gds.graph.nodeProperties.stream('{graph_obj.name()}',['{embedding_method}','SAB_CAT'],{graph_obj.node_labels()}, {{ listNodeLabels: true }})
    YIELD nodeId,nodeProperty,propertyValue,nodeLabels RETURN * """
    res = gds.run_cypher(query_get_props)
    res.index = res.nodeId  # Pivot df so that properties are columns 
    res['nodeLabels'] = [i[0] for i in res['nodeLabels']]
    rnz = pd.pivot(res,columns='nodeProperty',values='propertyValue')
    rnz['nodeId'] = rnz.index
    rnz = pd.merge(rnz,res[res.index.duplicated(keep='first')][['nodeLabels']], left_index=True, right_index=True).drop('nodeId',axis=1)
    
    rnz.reset_index(drop=True,inplace=True)
    
    unique_embeddings = len(np.unique(rnz[embedding_method]))  
    print(f'{embedding_method}:  # of unique embeddings: {unique_embeddings} out of {len(rnz)} total nodes\nusing {np.shape(rnz[embedding_method][0])} dimensions.')

    # JUST PLOT PCA-REDUCED EMBEDDINGS W/O COLORS/LABELS
    if plot_by=='None':
        df_emb = pd.DataFrame(rnz[embedding_method].tolist(), index= rnz.index).T
        pca = PCA(n_components=2,svd_solver='full'); pca.fit(df_emb)

        plot_map = pd.DataFrame(pca.components_,index=['pca1','pca2']).T; assert len(plot_map) == len(res)
        plt.figure(figsize=(5,5))
        plt.scatter(plot_map['pca1'], plot_map['pca2'], s=1)#,c=plot_map['colors'])


    colors = ['k','r','b','c']

    if plot_by=='NODE_LABEL':
        plt.figure(figsize=(5,5))
        ax_list = []
        labels_list = []
        DISTINCT_NODE_LABELS=rnz.nodeLabels.drop_duplicates()
        for N,LABEL in enumerate(DISTINCT_NODE_LABELS):
            #print(N,LABEL)
            df_temp = rnz[rnz['nodeLabels']==LABEL]
            df_emb = pd.DataFrame(df_temp[embedding_method].tolist(), index= df_temp.index).T
            pca = PCA(n_components=2,svd_solver='full'); pca.fit(df_emb)
            print()
            plot_map = pd.DataFrame(pca.components_,index=['pca1','pca2']).T; assert len(plot_map) == len(df_temp)
            #print(np.shape(plot_map))
            ax = plt.scatter(plot_map['pca1'], plot_map['pca2'], s=1, marker='o', color=colors[N])
            ax_list.append(ax)
            labels_list.append(LABEL)
        plt.legend(ax_list,labels_list,title=plot_by)

    
    if plot_by=='SAB_CAT':
        plt.figure(figsize=(5,5))
        ax_list = []
        sab_cat_list = []
        DISTINCT_SAB_CAT=rnz.SAB_CAT.drop_duplicates()
        for N,SAB_CAT in enumerate(DISTINCT_SAB_CAT):
                #print(N,SAB_CAT)   
                df_temp = rnz[rnz['SAB_CAT']==SAB_CAT]
                df_emb = pd.DataFrame(df_temp[embedding_method].tolist(), index= df_temp.index).T
                pca = PCA(n_components=2,svd_solver='full'); pca.fit(df_emb)
                plot_map = pd.DataFrame(pca.components_,index=['pca1','pca2']).T; assert len(plot_map) == len(df_temp)
                ax = plt.scatter(plot_map['pca1'], plot_map['pca2'], s=1, marker='o', color=colors[N])
                ax_list.append(ax)
                sab_cat_list.append(SAB_CAT)  
                
        plt.legend(ax_list,sab_cat_list,title=plot_by)
    #print(pca.explained_variance_ratio_)
    plt.xlabel(np.round(pca.explained_variance_ratio_[0]*100,2))
    plt.ylabel(np.round(pca.explained_variance_ratio_[1]*100,2))
        


