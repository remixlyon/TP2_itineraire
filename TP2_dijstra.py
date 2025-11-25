import csv
import networkx as nx

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

def dijkstra(graph, start, end):
    # Distance to each node (infinite by default)
    distances = {node: float('inf') for node in graph}
    distances[start] = 0

    # Keep track of the optimal path
    previous = {node: None for node in graph}

    # Visited set
    visited = set()

    while len(visited) < len(graph):
        # Pick the unvisited node with the smallest distance
        current = min(
            (node for node in graph if node not in visited),
            key=lambda node: distances[node]
        )

        visited.add(current)

        # Stop early if we reached the target
        if current == end:
            break

        # Update neighbors
        for neighbor, weight in graph[current].items():
            if neighbor in visited:
                continue

            new_distance = distances[current] + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current

    # Reconstruct path
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = previous[node]

    path.reverse()
    return path, distances[end]

if __name__ == "__main__":
    # import sommets data, aretes data et l'image
    matrice_sommets = charger_csv_en_matrice("TP2_position.csv")
    matrice_aretes = charger_csv_en_matrice("TP2_liaison.csv")

    # creer sommets dict
    sommets = charger_sommets(matrice_sommets)

    # creer graphe
    G=creer_graphe(matrice_aretes)

    distances = {node: float('inf') for node in G}
    print(distances)

    previous = {node: None for node in G}
    print(previous)

    visited = set()
    print(visited)

    poids = G.get_edge_data('Paris', 'Rouen').get('cout')
    print(poids)