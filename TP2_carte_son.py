import csv
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def charger_csv_en_matrice(nom_fichier):
    matrice = []
    with open(nom_fichier, mode='r', encoding='utf-8') as f:
        lecteur = csv.reader(f, delimiter=';')
        for ligne in lecteur:
            if ligne:
                matrice.append(ligne)
    return matrice

def charger_sommets(matrice_position):
    sommets = {}
    
    # Noter l'indexe de chaque champ
    header = matrice_position[0]
    idx_ville = header.index('ville')
    idx_x = header.index('posX')
    idx_y = header.index('posY')

    # Noter chaque ville à partir de la 2ème ligne et ajouter dans le dictionnaire
    for ligne in matrice_position[1:]:
        ville = ligne[idx_ville]
        x = float(ligne[idx_x])
        y = float(ligne[idx_y])
        sommets[ville] = (x, y)
    
    return sommets

def creer_graphe(matrice_aretes):
    G = nx.Graph()
    header = matrice_aretes[0]
    
    # Noter l'indexe de chaque champ
    idx_v1 = header.index('Ville1')
    idx_v2 = header.index('ville2')
    idx_type = header.index('type')
    idx_duree = header.index('duree')
    idx_cout = header.index('cout')

    # pour chaque ligne, ajoute une liaison entre 2 villes
    for ligne in matrice_aretes[1:]:
        ville1 = ligne[idx_v1]
        ville2 = ligne[idx_v2]
        type_liaison = ligne[idx_type]
        duree = float(ligne[idx_duree])
        cout = float(ligne[idx_cout])
        G.add_edge(ville1, ville2, type=type_liaison, duree=duree, cout=cout)
    return G

def dessiner_graphe_sur_carte(
    graphe, 
    sommets, 
    chemin_image_carte, 
    titre, 
    show_cout=False, 
    show_duree=False, 
    show_plot=True
):

    # read image
    img = mpimg.imread(chemin_image_carte)

    # size canvas
    plt.rcParams["figure.figsize"] = (10, 10)
    fig, ax = plt.subplots()
    
    # display image
    ax.imshow(img, cmap="gray")
    ax.axis('off')

    # edge colors
    couleurs_aretes = [
        'red' if graphe.edges[u, v]['type'] == 'a' else 'green'
        for u, v in graphe.edges()
    ]

    # draw graph
    nx.draw_networkx(
        graphe,
        pos=sommets,
        ax=ax,
        edge_color=couleurs_aretes,
        font_size=10,
        width=2
    )

    # optional edge labels
    if show_cout:
        edge_labels = {(u, v): f"{d['cout']}€" for u, v, d in graphe.edges(data=True)}
        nx.draw_networkx_edge_labels(
            graphe,
            pos=sommets,
            edge_labels=edge_labels,
            font_size=6,
            ax=ax
        )

    if show_duree:
        edge_labels = {(u, v): f"{d['duree']}m" for u, v, d in graphe.edges(data=True)}
        nx.draw_networkx_edge_labels(
            graphe,
            pos=sommets,
            edge_labels=edge_labels,
            font_size=6,
            ax=ax
        )

    # title
    plt.title(titre)

    # show or skip depending on flag
    if show_plot:
        plt.show()

    # return figure and axis if needed for embedding in UI
    return fig, ax

def dessiner_graphe_sur_carte_avec_chemin(
    chemin: list,
    graphe,
    sommets,
    chemin_image_carte,
    critere,
    contrainte="",
    show_plot=True
):

    img = mpimg.imread(chemin_image_carte)
    plt.rcParams["figure.figsize"] = (10, 10)
    fig, ax = plt.subplots()
    ax.imshow(img, cmap="gray")
    ax.axis('off')

    # Draw the whole graph in light gray
    nx.draw_networkx(
        graphe,
        pos=sommets,
        ax=ax,
        node_color='gray',
        edge_color='lightgray',
        font_size=10,
        width=1
    )

    # Highlight the path nodes
    nx.draw_networkx_nodes(
        graphe,
        pos=sommets,
        ax=ax,
        nodelist=chemin,
        node_color='red'
    )

    # Determine edges to highlight
    aretes_chemin = []
    couleurs_aretes = []
    total_cout, total_duree = 0, 0

    for i in range(len(chemin) - 1):
        u, v = chemin[i], chemin[i + 1]
        data = graphe.get_edge_data(u, v)
        if not data:
            continue  # no edge, skip
        aretes_chemin.append((u, v))
        color = 'red' if data['type'] == 'a' else 'green'
        couleurs_aretes.append(color)
        total_cout += data['cout']
        total_duree += data['duree']

    # Highlight path edges
    nx.draw_networkx_edges(
        graphe,
        pos=sommets,
        ax=ax,
        edgelist=aretes_chemin,
        edge_color=couleurs_aretes,
        width=4
    )

    # Edge labels depending on criterion
    if critere == 'cout':
        edge_labels = {(u, v): f"{graphe.edges[u, v]['cout']}€" for u, v in aretes_chemin}
    else:
        edge_labels = {(u, v): f"{graphe.edges[u, v]['duree']}m" for u, v in aretes_chemin}

    nx.draw_networkx_edge_labels(
        graphe,
        pos=sommets,
        edge_labels=edge_labels,
        font_size=6,
        ax=ax
    )

    # Title with constraint and total info
    total_detail = f"Durée={total_duree}m, Coût={total_cout:.2f}€"
    plt.title(f"{chemin[0]} -> {chemin[-1]} {contrainte}: {total_detail}")

    if show_plot:
        plt.show()

    # Return figure/axis for embedding in UI
    return fig, ax

def meilleur_chemin(graphe, ville_depart, ville_arrivee, critere) -> list:
    try:
        meilleur_chemin = nx.shortest_path(graphe, source=ville_depart, target=ville_arrivee, weight=critere)
    except nx.NetworkXNoPath:
        print(f"Aucun chemin n'existe entre {ville_depart} et {ville_arrivee}.")
        return [ville_depart,ville_arrivee]
    return meilleur_chemin

def filtre_graphe(graphe_initiale, type_a_exclure):
    G_filtre = nx.Graph()
    G_filtre.add_nodes_from(graphe_initiale.nodes())
    
    for u, v, data in graphe_initiale.edges(data=True):
        if data['type'] != type_a_exclure:
            G_filtre.add_edge(u, v, **data)
    return G_filtre


if __name__ == "__main__":
    # import sommets data, aretes data et l'image
    matrice_sommets = charger_csv_en_matrice("TP2_position.csv")
    matrice_aretes = charger_csv_en_matrice("TP2_liaison.csv")
    chemin_image_carte = "carte.jpg"

    # creer sommets dict
    sommets = charger_sommets(matrice_sommets)

    # creer graphe
    G=creer_graphe(matrice_aretes)
    
    dessiner_graphe_sur_carte(G, sommets, chemin_image_carte, "carte initiale")

    # ==============================================
    
    # Q1
    if nx.is_connected(G):
        connexe = "est connexe"
    else: connexe = "n'est pas connexe"
    dessiner_graphe_sur_carte(G, sommets, chemin_image_carte, f"graphe {connexe}")

    # Q2 - chemin le plus court
    ville_depart="Paris"
    ville_arrivee="Rennes"
    print("Q2: chemin le plus court")
    chemin_duree = meilleur_chemin(graphe=G, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='duree')
    print(chemin_duree)
    dessiner_graphe_sur_carte_avec_chemin(chemin_duree, G, sommets, chemin_image_carte, critere='duree')

    # Q3 - chemin le moins cher
    ville_depart="Paris"
    ville_arrivee="Marseille"
    print("Q3: chemin le moins cher")
    chemin_cout = meilleur_chemin(graphe=G, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='cout')
    dessiner_graphe_sur_carte_avec_chemin(chemin_cout, G, sommets, chemin_image_carte, critere='cout')

    # Q4 - chemin le plus court SANS autoroutes
    ville_depart="Paris"
    ville_arrivee="Rouen"
    
    G_filtre = filtre_graphe(G,'a')
    dessiner_graphe_sur_carte(G_filtre, sommets, chemin_image_carte, "carte sans autoroutes")
    
    print("Q4 - chemin le plus court SANS autoroutes")
    chemin_duree_sans_a = meilleur_chemin(graphe=G_filtre, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='duree')
    dessiner_graphe_sur_carte_avec_chemin(chemin_duree_sans_a, G_filtre, sommets, chemin_image_carte, critere='duree', contrainte="sans autoroutes")


    # Q5 - chemin le moins cher SANS départementales
    ville_depart="Paris"
    ville_arrivee="Marseille"
    
    G_filtre = filtre_graphe(G,'d')
    dessiner_graphe_sur_carte(G_filtre, sommets, chemin_image_carte, "carte sans départementales")

    print("Q5 - chemin le moins cher SANS départementales")
    chemin_cout_sans_d = meilleur_chemin(graphe=G_filtre, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='cout')
    dessiner_graphe_sur_carte_avec_chemin(chemin_cout_sans_d, G_filtre, sommets, chemin_image_carte, critere='cout', contrainte="sans départementales")

    
    


    
    


    
