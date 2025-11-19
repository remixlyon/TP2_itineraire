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

if __name__ == "__main__":
    # import sommets data
    matrice_sommets = charger_csv_en_matrice("TP2_position.csv")
    print(matrice_sommets)

    # import arêtes data
    matrice_aretes = charger_csv_en_matrice("TP2_liaison.csv")
    print(matrice_aretes)

    # creer sommets dict
    sommets = charger_sommets(matrice_sommets)
    print(sommets)

    # creer graphe
    G=creer_graphe(matrice_aretes)

    plt.rcParams["figure.figsize"] = (10, 10)
    fig, ax = plt.subplots()

    # Cela inverse l'image et la carte. C'est due à la différence entre nx et matlab
    img = mpimg.imread("carte.jpg")
    ax.imshow(img,cmap="gray")

    nx.draw_networkx(G,pos=sommets,ax=ax)
    plt.show()


    
