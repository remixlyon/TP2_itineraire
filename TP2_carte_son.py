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

def dessiner_graphe_sur_carte(graphe, sommets, chemin_image_carte, titre, show_cout=False, show_duree=False):
    # lire l'image
    img = mpimg.imread(chemin_image_carte)

    # size canvas = 10x10
    plt.rcParams["figure.figsize"] = (10, 10)

    # ax = plot zone
    fig, ax = plt.subplots()
    
    # afficher img dans ax, couleur grise, cela inverse le graphe
    ax.imshow(img,cmap="gray")
    
    # arete autoroute = red, arte departemental = green
    couleurs_aretes = []
    for u, v in graphe.edges():
        if graphe.edges[u, v]['type'] == 'a':
            couleurs_aretes.append('red')
        else:
            couleurs_aretes.append('green')

    # utilisant nx, dessiner le graphe
    nx.draw_networkx(
        graphe, # réseau des liaisons
        pos=sommets, # sommets
        ax=ax, # plot
        edge_color=couleurs_aretes,
        font_size=10,
        width=2
    )

    if show_cout == True:
        edge_labels = {(u, v): f"{d['cout']}€" for u, v, d in graphe.edges(data=True)}
        nx.draw_networkx_edge_labels(
            graphe,
            pos=sommets,
            edge_labels=edge_labels,
            font_size=6,
            ax=ax
        )

    if show_duree == True:
        edge_labels = {(u, v): f"{d['duree']}m" for u, v, d in graphe.edges(data=True)}
        nx.draw_networkx_edge_labels(
            graphe,
            pos=sommets,
            edge_labels=edge_labels,
            font_size=6,
            ax=ax
        )

    # afficher la zone (avec le plot ax)
    plt.title(f"{titre}")
    plt.show()

def dessiner_graphe_sur_carte_avec_chemin(chemin: list, graphe, sommets, chemin_image_carte, critere, contrainte = ""):
    img = mpimg.imread(chemin_image_carte)
    
    plt.rcParams["figure.figsize"] = (10, 10)
    fig, ax = plt.subplots()
    ax.imshow(img,cmap="gray")
   
    # utilisant nx, dessiner le graphe, couleur grise pour highlight plus tard
    nx.draw_networkx(
        graphe, # réseau des liaisons
        pos=sommets, # sommets
        ax=ax, # plot
        node_color='gray',
        edge_color='lightgray',
        font_size=10,
        width=1
    )
    
    # Surligner les sommets du chemin
    nx.draw_networkx_nodes(
        graphe,
        pos=sommets,
        ax=ax,
        nodelist=chemin,
        node_color='red'
    )

    # Si le "chemin" retourné par la fonction nx customisée ne contient que 2 sommets => checker si c'est le cas "aucune route"
    if len(chemin)==2:
        if graphe.has_edge(chemin[0], chemin[1]):
            # Calcul du coût et de la durée
            print(f"--- Itinéraire: {' -> '.join(chemin)} ---")

            data = graphe.get_edge_data(chemin[0], chemin[1])
            if data['type'] == 'a':
                type_route = "Autoroute"
            else: type_route = "Departementale"
            print(f"-1: {chemin[0]} -> {chemin[1]} - {type_route} - Durée = {data['duree']}; Cout = {data['cout']};")
                
            print(f"    Durée totale : {data['duree']} minutes")
            print(f"    Coût total : {data['cout']:.2f} €")
            print()

            # Surligner les arêtes du chemin
            nx.draw_networkx_edges(
                graphe,
                pos=sommets,
                ax=ax,
                edgelist=[chemin,],
                edge_color='red' if data['type'] == 'a' else 'green',
                width=4
            )

            detail = f"meilleur coût = {data['cout']}€" if critere=='cout' else f"meilleur temps = {data['duree']} minutes"
            plt.title(f"{chemin[0]} -> {chemin[-1]} {contrainte}: {detail}")
        else:
            plt.title(f"{chemin[0]} -> {chemin[-1]} {contrainte}: pas de route")
    else:
        # Calcul du coût et de la durée
            total_duree = 0
            total_cout = 0
            aretes_chemin = []
            couleurs_aretes = []
            print(f"--- Itinéraire: {' -> '.join(chemin)} ---")
            for i in range(len(chemin) - 1):
                u = chemin[i]
                v = chemin[i+1]
                data = graphe.get_edge_data(u, v)
                if data['type'] == 'a':
                    type_route = "Autoroute"
                else: type_route = "Departementale"
                print(f"-{i+1}: {u} -> {v} - {type_route} - Durée = {data['duree']}; Cout = {data['cout']};")

                total_duree += data['duree']
                total_cout += data['cout']
                aretes_chemin.append((u, v))

                if data['type'] == 'a':
                    couleurs_aretes.append('red')
                else:
                    couleurs_aretes.append('green')
                
            print(f"    Durée totale : {total_duree} minutes")
            print(f"    Coût total : {total_cout:.2f} €")
            print()

            # Surligner les arêtes du chemin
            nx.draw_networkx_edges(
                graphe,
                pos=sommets,
                ax=ax,
                edgelist=aretes_chemin,
                edge_color=couleurs_aretes,
                width=4
            )

            detail = f"meilleur coût = {round(total_cout,2)}€" if critere=='cout' else f"meilleur temps = {round(total_duree,2)} minutes"
            plt.title(f"{chemin[0]} -> {chemin[-1]} {contrainte}: {detail}")

    # Afficher cout / durée sur la carte
    if critere == 'cout':
        edge_labels = {(u, v): f"{d['cout']}€" for u, v, d in graphe.edges(data=True)}
        nx.draw_networkx_edge_labels(
            graphe,
            pos=sommets,
            edge_labels=edge_labels,
            font_size=6,
            ax=ax
        )
    else:
        edge_labels = {(u, v): f"{d['duree']}m" for u, v, d in graphe.edges(data=True)}
        nx.draw_networkx_edge_labels(
            graphe,
            pos=sommets,
            edge_labels=edge_labels,
            font_size=6,
            ax=ax
        )

    plt.show()

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
    ville_arrivee="Havre"
    
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

    
    


    
    


    
