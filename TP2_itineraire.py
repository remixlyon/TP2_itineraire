import csv
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import sys # Utiliser pour gérer les valeurs maximum


# 1. Ecrire une fonction qui prend en entrée un fichier (format .csv) et qui 
#    retourne les informations sous forme de matrice (array).

# ÉTAPE 1 :Lire le fichier CSV et retourner un array/liste
def charger_csv(nom_fichier):
    matrice = []
    with open(nom_fichier, mode='r', encoding='utf-8') as f:
        lecteur = csv.reader(f, delimiter=';')
        # Lire toutes les lignes
        for ligne in lecteur:
            if ligne:
                matrice.append(ligne)
    return matrice


# 2. Ecrire une fonction qui prend en entrée le tableau contenant les 
#    informations du fichier TP2-liaison.csv, et qui retourne le graphe correspondant.
# ÉTAPE 2 : Créer le graphe à partir des liaisons

def creer_graphe(liaisons):
    # Créer un graphe vide non orienté
    G = nx.Graph()
    
    # On parcourt toutes les liaisons 
    for i in range(1, len(liaisons)):
        ligne = liaisons[i]
        
        # Extraire les informations 
        ville1 = ligne[0].strip()
        ville2 = ligne[1].strip()
        type_route = ligne[2].strip()
        duree = float(ligne[3].strip())
        cout = float(ligne[4].strip())
        
        # Ajouter l'arête avec ses attributs
        G.add_edge(ville1, ville2, 
                   type=type_route, 
                   duree=duree, 
                   cout=cout)
    
    return G


# ÉTAPE 3 : Afficher le graphe sur la carte

def afficher_graphe(positions, image, graphe):
    # Définir la taille de la figure
    plt.rcParams["figure.figsize"] = (60, 15)

    # Créer le dictionnaire des positions
    positions = {}
    for i in range(1, len(positions_data)):
        ligne = positions_data[i]
        ville = ligne[0].strip()
        x = float(ligne[1].strip())
        y = float(ligne[2].strip())
        positions[ville] = (x, y)
    
    # Charger et afficher l'image de fond
    img = Image.open(chemin_image)
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[0, img.width, img.height, 0])

    # Séparer les arêtes par type (autoroutes et départementales)
    autoroutes = []
    departementales = []
    
    for (u, v, data) in graphe.edges(data=True):
        if data['type'] == 'a':
            autoroutes.append((u, v))
        else:
            departementales.append((u, v))
    
    # Dessiner les autoroutes en rouge
    nx.draw_networkx_edges(graphe, positions, 
                          edgelist=autoroutes,
                          edge_color='red',
                          width=3,
                          alpha=0.7,
                          ax=ax)
    
    # Dessiner les départementales en vert
    nx.draw_networkx_edges(graphe, positions,
                          edgelist=departementales,
                          edge_color='green',
                          width=3,
                          alpha=0.7,
                          ax=ax)
    
    # Dessiner les nœuds (villes)
    nx.draw_networkx_nodes(graphe, positions,
                          node_color='blue',
                          node_size=500,
                          alpha=0.9,
                          ax=ax)
    
    # Ajouter les labels des villes
    nx.draw_networkx_labels(graphe, positions,
                           font_size=12,
                           font_weight='bold',
                           font_color='white',
                           ax=ax)


    # Désactiver les axes
    ax.axis('off')
    
    plt.title("Réseau routier français - Autoroutes (rouge) et Départementales (vert)", 
              fontsize=20, pad=20)
    plt.tight_layout()
    plt.show()

# ============================================
# PROGRAMME PRINCIPAL - EXEMPLE D'UTILISATION
# ============================================

if __name__ == "__main__":
    print("=== TP2 - Graphes : Planification d'itinéraire ===\n")
    
    # 1. Charger les données
    print("Étape 1 : Chargement des fichiers CSV...")
    liaisons = charger_csv('TP2_liaison.csv')
    positions_data = charger_csv('TP2_position.csv')
    print(f"✓ {len(liaisons)-1} liaisons chargées")
    print(f"✓ {len(positions_data)-1} villes chargées\n")
    
    # 2. Créer le graphe
    print("Étape 2 : Création du graphe...")
    G = creer_graphe(liaisons)
    print(f"✓ Graphe créé avec {G.number_of_nodes()} nœuds et {G.number_of_edges()} arêtes\n")
    
    # Afficher quelques informations sur le graphe
    print("Informations sur le graphe :")
    print(f"  - Villes : {list(G.nodes())[:5]}... (et {G.number_of_nodes()-5} autres)")
    
    # Exemple d'arête avec ses attributs
    exemple_arete = list(G.edges(data=True))[0]
    print(f"  - Exemple de liaison : {exemple_arete[0]} ↔ {exemple_arete[1]}")
    print(f"    Type: {exemple_arete[2]['type']}, Durée: {exemple_arete[2]['duree']} min, Coût: {exemple_arete[2]['cout']} €\n")
    
    # 3. Afficher le graphe sur la carte
    print("Étape 3 : Affichage du graphe sur la carte...")
    print("(Note : Vous devez avoir le fichier carte.jpg pour que l'affichage fonctionne)")
    
    # Décommenter la ligne suivante si vous avez l'image :
    # afficher_graphe(positions_data, 'carte.jpg', G)
    
    print("\n=== Partie 1 terminée avec succès ! ===")
