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

def dessiner_graphe_sur_carte(graphe, sommets, chemin_image_carte):
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

    # edge_labels = {(u, v): f"{d['cout']}€\n{d['duree']}h" for u, v, d in graphe.edges(data=True)}
    # nx.draw_networkx_edge_labels(
    #     graphe,
    #     pos=positions,
    #     edge_labels=edge_labels,
    #     font_size=6,
    #     ax=ax
    # )

        # Surligner les arêtes du chemin
    nx.draw_networkx_edges(
        graphe,
        pos=sommets,
        ax=ax,
        edgelist=[('Paris', 'Rennes'),('Rennes','Brest')],
        edge_color='blue',
        width=4
    )

    # afficher la zone (avec le plot ax)
    plt.show()

if __name__ == "__main__":
    # import sommets data, aretes data et l'image
    matrice_sommets = charger_csv_en_matrice("TP2_position.csv")
    matrice_aretes = charger_csv_en_matrice("TP2_liaison.csv")
    chemin_image_carte = "carte.jpg"

    # creer sommets dict
    sommets = charger_sommets(matrice_sommets)

    # creer graphe
    G=creer_graphe(matrice_aretes)
    
    print(nx.is_connected(G))

    ville_depart="Paris"
    ville_arrivee="Marseille"
    chemin_duree = nx.shortest_path(G, source=ville_depart, target=ville_arrivee, weight='duree')
    print(chemin_duree)

    dessiner_graphe_sur_carte(G, sommets, chemin_image_carte)

    


    
