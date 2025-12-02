"""
TP Graphe de Son NGUYEN & Rémi DEMOULIN
1) fonctions de base
2) main > 5 questions
3) main > bonus (mst, euler, exclure/imposer une ville)

"""

import csv
import heapq
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


# Fonction pour charger CSV en matrice (ignorer les lignes commençant par #)
def charger_csv_en_matrice(nom_fichier) -> list:
    matrice = []
    with open(nom_fichier, mode='r', encoding='utf-8') as f:
        lecteur = csv.reader(f, delimiter=';')
        for ligne in lecteur:
            if not ligne or ligne[0].startswith('#'):
                continue
            matrice.append(ligne)
    return matrice

# Fonction pour charger les sommets à partir d'une matrice
def charger_sommets(matrice_position) -> dict:
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

# Fonction pour charger les liaison à partir d'une matrice
def charger_liaisons(matrice_aretes) -> list:
    liaisons = []
    
    # Noter l'indexe de chaque champ
    header = matrice_aretes[0]
    idx_v1 = header.index('Ville1')
    idx_v2 = header.index('ville2')
    idx_type = header.index('type')
    idx_duree = header.index('duree')
    idx_cout = header.index('cout')

    # Extraire toutes les liaisons à partir de la 2ème ligne et ajouter dans le dictionnaire
    for ligne in matrice_aretes[1:]:
        ville1 = ligne[idx_v1]
        ville2 = ligne[idx_v2]
        type_liaison = ligne[idx_type]
        duree = float(ligne[idx_duree])
        cout = float(ligne[idx_cout])

        # Stocker ville1, ville2, data dans un tuple et ajouter le tuple dans la list
        liaisons.append(
            (ville1, ville2, {
                "type": type_liaison,
                "duree": duree,
                "cout": cout
            })
        )

    return liaisons

# Fonction pour créer le graphe à partir des sommets & liaisons
def creer_graphe(sommets, liaisons):
    G = nx.Graph()

    # add_node prend en input dict (sommet:[x,y], ...)
    for ville, xy in sommets.items():
        G.add_node(ville, xy=xy)

    # add_edges_from prend en input une liste (sommet1, sommet2, {data1,data2 ...})
    G.add_edges_from(liaisons)

    return G

# Fonction pour dessiner le graphe sur le JPG
def dessiner_graphe_sur_carte(graphe, chemin_image_carte, titre, show_cout=False, show_duree=False, export_path=None):
    # lire l'image
    img = mpimg.imread(chemin_image_carte)

    # paraméter la taille par défaut de la figure
    plt.rcParams["figure.figsize"] = (10, 10)

    # création de la figure avec la zone dessin ax
    fig, ax = plt.subplots()
    
    # afficher img dans ax, couleur grise (sinon jaune-vert), cela inverse le graphe
    ax.imshow(img,cmap="gray")
    
    # arete autoroute = red, arte departemental = green
    couleurs_aretes = []
    for u, v in graphe.edges():
        if graphe.edges[u, v]['type'] == 'a':
            couleurs_aretes.append('red')
        else:
            couleurs_aretes.append('green')

    # utilisant nx, dessiner le graphe (nx.draw est plus simple mais moins fine)
    nx.draw_networkx(
        graphe, # réseau des liaisons
        pos=nx.get_node_attributes(graphe, 'xy'), # sommets
        ax=ax, # plot
        edge_color=couleurs_aretes,
        font_size=10,
        width=2
    )

    # afficher le cout sur les aretes
    if show_cout == True:
        edge_labels = {(u, v): f"{d['cout']}€" for u, v, d in graphe.edges(data=True)}
        nx.draw_networkx_edge_labels(
            graphe,
            pos=nx.get_node_attributes(graphe, 'xy'), # sommets
            edge_labels=edge_labels,
            font_size=5,
            ax=ax
        )

    # afficher la duree sur les aretes
    if show_duree == True:
        edge_labels = {(u, v): f"{d['duree']}m" for u, v, d in graphe.edges(data=True)}
        nx.draw_networkx_edge_labels(
            graphe,
            pos=nx.get_node_attributes(graphe, 'xy'), # sommets
            edge_labels=edge_labels,
            font_size=5,
            ax=ax
        )

    # afficher le titre pour le plot
    plt.title(f"{titre}")

    # exporter en jpg
    if export_path is not None:
        plt.savefig(export_path, format='jpg', dpi=300)

    # afficher le plot avec la figure
    plt.show()

# Fonction pour dessiner le graphe sur le JPG et tracer le chemin
def dessiner_graphe_sur_carte_avec_chemin(chemin: list, graphe, chemin_image_carte, critere, poids_total, titre, contrainte = '', direction=False, export_path=None):
    """
    Cas particuliers du 'chemin':
    - len == 1 : chemin = le msg d'erreur comme quoi les villes départ et arrivée ne sont pas valides
    - poids_total == 0 : pas de route entre les 2 villes
    """
    
    # redessiner la carte
    img = mpimg.imread(chemin_image_carte)
    plt.rcParams["figure.figsize"] = (10, 10)
    fig, ax = plt.subplots()
    ax.imshow(img,cmap="gray")
   
    # utilisant nx, dessiner le graphe, couleur grise pour highlight plus tard
    nx.draw_networkx(
        graphe,
        pos=nx.get_node_attributes(graphe, 'xy'), # sommets
        ax=ax,
        node_color='gray',
        edge_color='lightgray',
        font_size=10,
        width=1
    )

    # Surligner en rouge les sommets intermédiaires du chemin
    if len(chemin) >=2 :
        nx.draw_networkx_nodes(
            graphe,
            pos=nx.get_node_attributes(graphe, 'xy'), # sommets
            ax=ax,
            nodelist=chemin[1:-1],
            node_color='red'
        )

        # Surligner en blue les extrémités du chemin
        nx.draw_networkx_nodes(
            graphe,
            pos=nx.get_node_attributes(graphe, 'xy'), # sommets
            ax=ax,
            nodelist=[chemin[0],chemin[-1]],
            node_color='blue'
        )

    # poid != 0, un chemin est trouvé
    if poids_total!=0:
        aretes_chemin = []
        couleurs_aretes = []
        for i in range(len(chemin) - 1):
            u = chemin[i]
            v = chemin[i+1]
            data = graphe.get_edge_data(u, v)

            aretes_chemin.append((u, v))

            if data['type'] == 'a':
                couleurs_aretes.append('red')
            else:
                couleurs_aretes.append('green')

        # Surligner les arêtes du chemin
        nx.draw_networkx_edges(
            graphe,
            pos=nx.get_node_attributes(graphe, 'xy'), # sommets
            ax=ax,
            edgelist=aretes_chemin,
            edge_color=couleurs_aretes,
            width=3,
            arrows=direction
        )

        # Afficher cout / durée sur la carte
        if critere == 'cout':
            edge_labels = {(u, v): f"{d['cout']}€" for u, v, d in graphe.edges(data=True)}
            nx.draw_networkx_edge_labels(
                graphe,
                pos=nx.get_node_attributes(graphe, 'xy'), # sommets
                edge_labels=edge_labels,
                font_size=5,
                ax=ax
            )
            plt.title(f"{chemin[0]} -> {chemin[-1]} {contrainte}: {titre}. Cout total = {round(poids_total,2)}€")
        else:
            edge_labels = {(u, v): f"{d['duree']}m" for u, v, d in graphe.edges(data=True)}
            nx.draw_networkx_edge_labels(
                graphe,
                pos=nx.get_node_attributes(graphe, 'xy'), # sommets
                edge_labels=edge_labels,
                font_size=5,
                ax=ax
            )
            plt.title(f"{chemin[0]} -> {chemin[-1]} {contrainte}: {titre}. Duree totale = {int(poids_total // 60)}h {int(poids_total % 60)} minutes")

    # si 'chemin' ne contient qu'un élément => c'est juste le msg d'erreur
    elif poids_total==0 and len(chemin)==1:
        plt.title(f"{chemin[0]}")

    # poid == 0, len == 2 (juste les 2 villes) => pas de route
    else:
        plt.title(f"{chemin[0]} -> {chemin[-1]} {contrainte}: pas de route")

    if export_path is not None:
        plt.savefig(export_path, format='jpg', dpi=300)
    plt.show()

# Fonction pour trouver le meilleur chemin (remplaçant manuel de nx.shortest_path)
def meilleur_chemin(graphe, ville_depart, ville_arrivee, critere, debug=False) -> tuple[list, float]:
    """
    Cas de retour particuliers:
    - chemin = msg, poid = 0 : ville(s) invalides
    - chemin = 2, poid = 0 : pas de route
    """
    
    # nx.shortest_path(graphe, ville_depart, ville_arrivee, critere)

    # Manuel
    # Etape 0: vérifier si les villes données sont valides
    if ville_depart not in graphe:
        msg = f"    {ville_depart} n'est pas présente dans la carte"
        print(msg)        
        return [msg],0
    if ville_arrivee not in graphe:
        msg = f"    {ville_arrivee} n'est pas présente dans la carte"
        print(msg)        
        return [msg],0
    if ville_depart==ville_arrivee:
        msg = f"Même ville ({ville_depart}) - Métro boulot dodo ?"
        print(msg)        
        return [msg],0
    
    # Etape 1: 
    # donner un poid infini à tous les sommets sauf ville_depart à 0
    distances = {ville: float('inf') for ville in graphe.nodes}
    distances[ville_depart] = 0
    # initier un dict pour noter les meilleurs 'sommet-1'
    predecesseurs = {ville: None for ville in graphe.nodes}

    # Etape 2. Boucle principale de Dijkstra
    # File de priorité: (distance_actuelle, ville_actuelle)
    pq = [(0, ville_depart)] 
    if debug: print(f'>> START: départ de {ville_depart}') 
    while pq:
        # Extraire le sommet non visité avec la plus petite distance
        dist_nouvelle, u = heapq.heappop(pq)
        if debug: print(f'>> Explorer les voisins de {u} ({dist_nouvelle}): {list(graphe.neighbors(u))}') 

        # Si nous avons déjà trouvé un chemin plus court pour 'u', ignorer cette entrée et reprendre la boucle WHILE
        if dist_nouvelle > distances[u]:
            if debug: print(f'>>    [IGNORE] On a déjà une distance plus petite pour {u} (actuelle {distances[u]}; nouvelle {dist_nouvelle})') 
            continue
        
        # Si la destination est atteinte, STOP la boucle While
        if u == ville_arrivee:
            if debug: print(f'>> STOP: Arrivé à {u}') 
            break

        # 2a. On examine chaque sommet voisin
        for v in graphe.neighbors(u):
            # Récupérer le poids de l'arête (critère durée ou coût)
            poids = graphe.get_edge_data(u, v).get(critere, float('inf'))
            if debug: print(f'>>    De {u} à {v}: distance = {poids}') 
            
            nouvelle_distance = dist_nouvelle + poids
            if debug: print(f'>>    Nouvelle distance de {v} par rapport à {ville_depart} = {nouvelle_distance}')
            if debug: print(f'>>    Pour {v}, on compare la distance notée ({distances[v]}) et la nouvelle distance ({nouvelle_distance})') 

            # 2b. Mettre à jour le poid du voisin v si on trouve un chemin plus court vers lui
            if nouvelle_distance < distances[v]:
                distances[v] = nouvelle_distance
                if debug: print(f'>>    [MAJ] Pour {v}, la nouvelle distance trouvée est meilleure ({nouvelle_distance})') 

                predecesseurs[v] = u
                if debug: print(f'>>    [MAJ] Mettre à jour le chemin vers {v} en passant par {u}\n') 
                heapq.heappush(pq, (nouvelle_distance, v))
            else: 
                if debug: print(f'>>    [IGNORE] Pour {v}, la distance notée est meilleure ({distances[v]})\n') 


    # 3. Reconstruction du chemin
    # si la distance de la ville arrivee n'est pas modifiée, aucun chemin n'est trouvé
    meilleur_chemin = []
    if distances[ville_arrivee] == float('inf'):
        meilleur_chemin = [ville_depart,ville_arrivee]
        poids_total = 0
        print(f"    Aucun chemin n'existe entre {ville_depart} et {ville_arrivee}.")
        return meilleur_chemin, poids_total

    # en partir de la destination, reconstruire la chaine de predecesseurs
    ville_courante = ville_arrivee
    while ville_courante is not None:
        meilleur_chemin.append(ville_courante)
        ville_courante = predecesseurs[ville_courante]
    
    # Le chemin est reconstruit à l'envers, il faut donc l'inverser
    meilleur_chemin = meilleur_chemin[::-1]

    # poids total
    poids_total = distances[ville_arrivee]
    devise = '€' if critere=='cout' else ' minutes'

    for i in range(len(meilleur_chemin)-1):
        u = meilleur_chemin[i]
        v = meilleur_chemin[i+1]
        distance = graphe.get_edge_data(u, v).get(critere)
        type = poids = graphe.get_edge_data(u, v).get('type')
        print(f'    {u} -> {v} ({type}): {distance}{devise}')
    print(f'    *TOTAL* = {round(poids_total,2)}{devise}')

    # Rendre le chemin et la distance totale
    return meilleur_chemin, poids_total

# Fonction pour savoir si le graphe est connexe (remplaçant manuel de nx.is_connected)
def connexe_manuel(graphe) -> tuple[bool, list]:

    sommets_vu = set()  # liste des sommets déjà explorés
    continents = []  # liste des groupes de sommets isolés

    for ville_depart in graphe.nodes():

        # ignorer les villes déjà explorées
        if ville_depart in sommets_vu:
            continue

        print(f"    [CONTINENT] {ville_depart}")

        stack = [ville_depart]              # liste des villes à explorer
        continent = set([ville_depart])     # set des villes d'un continent
        sommets_vu.add(ville_depart)        # set des villes explorées

        # exploration d'un continent
        while stack:
            # node = stack.pop()              # LIFO (DSF)
            node = stack.pop(0)              # FIFO (BSF) - moins performant car list (index shifting après pop)
            print(f"        Exploration à partir de: {node}")

            # ignorer les villes déjà explorées
            if all(neighbor in list(sommets_vu) for neighbor in graphe.neighbors(node)):
                print(f"            Tous ses voisins sont connectés")
                continue
            
            # explorer les villes voisines
            for ville in graphe.neighbors(node):
                if ville not in sommets_vu:
                    sommets_vu.add(ville)
                    continent.add(ville)
                    stack.append(ville)
                    # print(stack)
                    # afficher l'avancement
                    print(f"            {ville} est connectée")

        # ajouter le continent dans la liste des continents 
        continents.append(continent)

    # Graphe est connexe s'il y a un seul continent
    est_connexe = (len(continents) == 1)

    return est_connexe, continents

def filtre_graphe(graphe_initiale, type_a_exclure=None, ville_a_exclure=[]):
    G_filtre = nx.Graph()
    
    for node, data in graphe_initiale.nodes(data=True):
        if node not in ville_a_exclure:
            G_filtre.add_node(node, **data)
    
    for u, v, data in graphe_initiale.edges(data=True):
        if u not in ville_a_exclure and v not in ville_a_exclure:
            if data['type'] != type_a_exclure:
                G_filtre.add_edge(u, v, **data)
    return G_filtre



# # BONUS 2: lister tous les bons chemins (nx)
# def meilleur_chemin_all(graphe, ville_depart, ville_arrivee, critere) -> list:
#     try:
#         meilleur_chemin_all = nx.all_shortest_paths(graphe, source=ville_depart, target=ville_arrivee, weight=critere)
#     except nx.NetworkXNoPath:
#         print(f"Aucun chemin n'existe entre {ville_depart} et {ville_arrivee}.")
#         return [ville_depart,ville_arrivee]
#     return meilleur_chemin_all

# # BONUS 3: lister tous les chemins (nx)
# def all_paths_with_costs(graphe, ville_depart, ville_arrivee, critere="cout"):
#     paths = list(nx.all_simple_paths(graphe, ville_depart, ville_arrivee))
#     results = []

#     for path in paths:
#         cost = 0
#         for u, v in zip(path[:-1], path[1:]):
#             cost += graphe[u][v][critere]   # sum the cost attribute

#         results.append((path, cost))

#     return results

# BONUS 4: Kruskal MST (manuel)
def find_mst(graphe, critere="cout", debug=False):
    # nx
    # T = nx.minimum_spanning_tree(graphe, weight=critere)
    
    # manuel
    # fonction pour détecter les boucles
    def boucle_check(T, sommet1, sommet2):
        sommets_vu = set()
        sommets_vu_ordre = []         # optimisation de perf
        stack = [sommet1]

        while stack:
            node = stack.pop()                  # LIFO (DSF)
            
            # s'il existe déjà un chemin de sommet1 vers sommet2
            if node == sommet2:
                return True, sommets_vu_ordre
            
            # explorer les villes voisines
            if node not in sommets_vu:
                sommets_vu.add(node)
                sommets_vu_ordre.append(node)
                for voisin in T.neighbors(node):
                    if voisin not in sommets_vu:
                        stack.append(voisin)
        return False, []

    T = nx.Graph()
    T.add_nodes_from(graphe.nodes(data=True))

    # ajouter les arêtes dans un heapq dans l'ordre croissant 
    heap = []
    for u, v, data in graphe.edges(data=True):
        poid = data[critere]
        heapq.heappush(heap, (poid, u, v, data))

    poids_total = 0

    while heap:
        poid, u, v, data = heapq.heappop(heap)
        
        # vérifier s'il forme une boucle
        boucle, boucle_chemin = boucle_check(T, u, v)
        if not boucle:
            T.add_edge(u, v, **data)
            poids_total += poid
            if debug: print(f'>>  [MAJ]     {poid}, {u} - {v}, {data}')
        else:
            if debug: print(f'>>  [IGNORE]  {u} - {v} aurait formé une boucle via {boucle_chemin[1:]}')

        # # Vrai seulement si full-connexe: Kruskal prend fin lors que le nombre d'arêtes = le nombre de sommets - 1
        # if T.number_of_edges() == graphe.number_of_nodes() - 1:
        #     break

    return T, poids_total

# BONUS 5: Euler (nx)
def find_euler(graphe, critere, ville_depart=None):
    aretes_euler_path = list(nx.eulerian_path(graphe,source=ville_depart))

    # Créer un graphe directionnel et copier les sommets du graphe initial
    DG = nx.DiGraph()
    DG.add_nodes_from(graphe.nodes(data=True))

    poids_total = 0
    # Ajouter les arêtes un par un et overwrite son poid par son ordre
    for order, (u, v) in enumerate(aretes_euler_path, start=1):
        attr = graphe[u][v].copy()
        poids_total += attr[critere]
        attr[critere] = order  # overwrite cout with Euler order
        DG.add_edge(u, v, **attr)

    nodes_euler_path = [aretes_euler_path[0][0]] + [v for u, v in aretes_euler_path]
    return DG, nodes_euler_path, poids_total

# # BONUS 6: Glouton (manuel - not finished)
# def glouton(graphe, debug=False) -> dict:
#     heap = []
#     for sommet in G.nodes():
#         degree = G.degree(sommet)
#         heapq.heappush(degree, sommet)

#     couleur = ['red', 'blue', 'green', 'yellow', 'black']
#     chromatique = {}

#     while heap:
#         degree, sommet = heapq.heappop(heap)
#         chromatique[sommet] = couleur[0]


#     # fonction pour détecter les boucles
#     def boucle_check(T, sommet1, sommet2):
#         sommets_vu = set()
#         sommets_vu_ordre = []         # optimisation de perf
#         stack = [sommet1]

#         while stack:
#             node = stack.pop()                  # LIFO (DSF)
            
#             # s'il existe déjà un chemin de sommet1 vers sommet2
#             if node == sommet2:
#                 return True, sommets_vu_ordre
            
#             # explorer les villes voisines
#             if node not in sommets_vu:
#                 sommets_vu.add(node)
#                 sommets_vu_ordre.append(node)
#                 for voisin in T.neighbors(node):
#                     if voisin not in sommets_vu:
#                         stack.append(voisin)
#         return False, []

#     T = nx.Graph()
#     T.add_nodes_from(graphe.nodes(data=True))

#     # ajouter les arêtes dans un heapq dans l'ordre croissant 
#     heap = []
#     for u, v, data in graphe.edges(data=True):
#         poid = data[critere]
#         heapq.heappush(heap, (poid, u, v, data))

#     poids_total = 0

#     while heap:
#         poid, u, v, data = heapq.heappop(heap)
        
#         # vérifier s'il forme une boucle
#         boucle, boucle_chemin = boucle_check(T, u, v)
#         if not boucle:
#             T.add_edge(u, v, **data)
#             poids_total += poid
#             if debug: print(f'>>  [MAJ]     {poid}, {u} - {v}, {data}')
#         else:
#             if debug: print(f'>>  [IGNORE]  {u} - {v} aurait formé une boucle via {boucle_chemin[1:]}')

#         # # Vrai seulement si full-connexe: Kruskal prend fin lors que le nombre d'arêtes = le nombre de sommets - 1
#         # if T.number_of_edges() == graphe.number_of_nodes() - 1:
#         #     break

#     return T, poids_total

# BONUS 7: 
def meilleur_chemin_escale(graphe, ville_depart, ville_escale, ville_arrivee, critere, debug=False) -> tuple[list, float]:
    chemin1, distance1 = meilleur_chemin(graphe, ville_depart, ville_escale, critere, debug=debug)
    chemin2, distance2 = meilleur_chemin(graphe, ville_escale, ville_arrivee, critere, debug=debug)

    if distance1 == 0 or distance2 == 0:
        return [ville_depart, ville_escale, ville_arrivee], 0

    chemin_total = chemin1 + chemin2[1:]
    distance_total = distance1 + distance2

    if debug:
        print(chemin1)
        print(chemin2)
        print(chemin_total)

    return chemin_total, distance_total




























if __name__ == "__main__":
    # import sommets data, aretes data et l'image
    matrice_sommets = charger_csv_en_matrice("TP2_position.csv")
    matrice_aretes = charger_csv_en_matrice("TP2_liaison.csv")
    chemin_image_carte = "carte.jpg"

    # creer sommets dict
    sommets = charger_sommets(matrice_sommets)
    liaisons = charger_liaisons(matrice_aretes)

    # creer graphe
    G=creer_graphe(sommets, liaisons)
  

    # =================================================================================================================================
    
    # Q1
    print(f"Q1: Le graphe est-il connexe ?")
    est_connexe, continents = connexe_manuel(G)
    if est_connexe:
        connexe = "est connexe"
    else: connexe = "n'est pas connexe"
    print(f"---> Le graphe {connexe}")
    print()
    print(f"Le graphe contient {len(continents)} groupe(s) connexe(s)")
    for continent in continents:
        print(f"    Continent {continents.index(continent)+1} contient {len(continent)} villes(s):")
        for ville in continent:
            print(f"    - {ville}")
        
    dessiner_graphe_sur_carte(G, chemin_image_carte, titre=f"graphe {connexe}", export_path="carte_initiale.jpg")



    # Q2 - chemin le plus court
    ville_depart="Paris"
    ville_arrivee="Bastia"

    # optimisation pour reduire le nombre de checks
    if not est_connexe:
        for continent in continents:
            if ville_depart in continent:
                continent_depart = continent
            if ville_arrivee in continent:
                continent_arrivee = continent
        if len(continent_depart) > len(continent_arrivee):
            tmp = ville_depart 
            ville_depart = ville_arrivee
            ville_arrivee = tmp

    print(f"Q2: Chemin le plus court entre {ville_depart} et {ville_arrivee}")
    chemin_duree, poids_total = meilleur_chemin(graphe=G, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='duree', debug=True)
    dessiner_graphe_sur_carte_avec_chemin(chemin_duree, G, chemin_image_carte, titre='chemin le plus court', critere='duree', poids_total=poids_total, export_path="chemin_temps.jpg")



    # Q3 - chemin le moins cher
    ville_depart="Paris"
    ville_arrivee="Marseille"
    print(f"Q3: Chemin le moins cher entre {ville_depart} et {ville_arrivee}")
    chemin_cout, poids_total = meilleur_chemin(graphe=G, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='cout', debug=True)
    dessiner_graphe_sur_carte_avec_chemin(chemin_cout, G, chemin_image_carte, titre='chemin le moins cher', critere='cout', poids_total=poids_total, export_path="chemin_cout.jpg")



    # Q4 - chemin le plus court SANS autoroutes
    ville_depart="Paris"
    ville_arrivee="Havre"
    
    print(f"Q4: Chemin le plus court entre {ville_depart} et {ville_arrivee} SANS autoroutes")
    G_filtre = filtre_graphe(G,'a')
    dessiner_graphe_sur_carte(G_filtre, chemin_image_carte, titre="Carte sans autoroutes", show_duree=True, export_path="carte_sans_autoroute_avec_duree.jpg")
    chemin_duree_sans_a, poids_total = meilleur_chemin(graphe=G_filtre, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='duree')
    dessiner_graphe_sur_carte_avec_chemin(chemin_duree_sans_a, G_filtre, chemin_image_carte, titre='chemin le plus court', critere='duree', poids_total=poids_total, contrainte="sans autoroutes", export_path="chemin_cout_no_a.jpg")

    # Q5 - chemin le moins cher SANS routes départementales
    ville_depart="Rouen"
    ville_arrivee="Nice"

    print(f"Q5: Chemin le moins cher entre {ville_depart} et {ville_arrivee} SANS routes départementales")
    G_filtre = filtre_graphe(G,'d')
    dessiner_graphe_sur_carte(G_filtre, chemin_image_carte, titre="Carte sans routes départementales", show_cout=True, export_path="carte_sans_dept_avec_cout.jpg")
    chemin_cout_sans_d, poids_total = meilleur_chemin(graphe=G_filtre, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='cout')
    dessiner_graphe_sur_carte_avec_chemin(chemin_cout_sans_d, G_filtre, chemin_image_carte, titre='chemin le moins cher', critere='cout', poids_total=poids_total, contrainte="sans routes départementales", export_path="chemin_temps_no_d.jpg")

    





















    # # =================================================================================================================================

    # # BONUS 1 - afficher le chemin le plus rapide et le chemin le moins cher sur le même graphe
    # ville_depart="Brest"
    # ville_arrivee="Marseille"

    # print(f"BONUS1: Chemin le moins cher vs. le plus rapide entre : {ville_depart} et {ville_arrivee}")
    # chemin_cout, cout_total = meilleur_chemin(graphe=G, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='cout')
    # chemin_duree, temps_total = meilleur_chemin(graphe=G, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='duree')
    
    # chemin_duree_inverse = list(reversed(chemin_duree))
    # if len(chemin_duree_inverse) > 2:
    #     chemin_duree_inverse = chemin_duree_inverse[1:]
    # chemin_total = chemin_cout + chemin_duree_inverse
    
    # dessiner_graphe_sur_carte_avec_chemin(chemin_total, G, chemin_image_carte, poids_total= 1, titre='time vs. money', critere='cout')


    # # BONUS 2 - afficher tous les "shortest paths"
    # ville_depart="Brest"
    # ville_arrivee="Nice"

    # meilleur_chemin_all = list(meilleur_chemin_all(graphe=G, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='cout'))
    # print(meilleur_chemin_all)




    # # BONUS 3 - afficher tous les chemins et leur coût. Filtre le graphe avant de lancer l'algo car trop de résultats sinon
    # ville_depart="Brest"
    # ville_arrivee="Nice"

    # # G_filtre = filtre_graphe(G,'a')
    # # dessiner_graphe_sur_carte(G_filtre, sommets, chemin_image_carte, "Carte sans autoroutes", show_duree=True, export_path="carte_sans_autoroute_avec_duree.jpg")

    # G_filtre = filtre_graphe(G,'d')
    # dessiner_graphe_sur_carte(G_filtre, chemin_image_carte, "Carte sans routes départementales", show_cout=True, export_path="carte_sans_dept_avec_cout.jpg")

    # result = all_paths_with_costs(graphe=G_filtre, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='cout')
    # # Afficher les 5 meilleurs chemins
    # result_sorted = sorted(result, key=lambda x: x[1])
    # for path in result_sorted[0:5]:
    #     print(path)


    # BONUS 4 - afficher l'arbre couvrant poid minimum (MST)
    print(f"Bonus 4a: Arbre couvrant au meilleur cout")
    T_cout, poids_total = find_mst(G,'cout', debug = True)
    print(f"====> Arbre couvrant au meilleur cout {round(poids_total,2)}€")
    dessiner_graphe_sur_carte(T_cout, chemin_image_carte, f"MST coût = {round(poids_total,2)}€", show_cout=True, export_path="mst_cout.jpg")

    print()

    print(f"Bonus 4b: Arbre couvrant au meilleur temps")
    T_duree, poids_total = find_mst(G,'duree', debug = True)
    print(f"====> Arbre couvrant au meilleur temps {poids_total} minutes")
    dessiner_graphe_sur_carte(T_duree, chemin_image_carte, f"MST durée = {poids_total} minutes", show_duree=True, export_path="mst_duree.jpg")

    

    # BONUS 5 - checker si le graphe est semi-euler / euler
    print(f"BONUS 5: Verif Euler - degré des sommets")
    for sommet in G.nodes():
        print(f"    {sommet} - {G.degree(sommet)} {'(impair)' if G.degree(sommet) % 2 ==1 else ''}")
    sommets_impairs = [x for x in G.nodes() if G.degree(x) % 2 == 1]
    print(f'Sommets impairs = {sommets_impairs}\n')
    for sommet in sommets_impairs:
        print(f"{sommet} - {G.degree(sommet)}")
    
    semieuler = nx.is_semieulerian(G)
    print(f"Graphe dispose d'un parcours euler ? {semieuler}")
    euler = nx.is_eulerian(G)
    print(f"Graphe dispose d'un cicuit euler ? {euler}")

    ville_depart = 'Nice'
    if euler:
        DG, chemin_euler, poids_total = find_euler(G, ville_depart=ville_depart, critere='cout')
        dessiner_graphe_sur_carte_avec_chemin(chemin_euler, DG, chemin_image_carte, poids_total=poids_total, titre=f"{'parcours' if semieuler else 'circuit'} Euler", critere='cout', direction=True, export_path="chemin_euler.jpg")
    
    if semieuler:
        DG, chemin_euler, poids_total = find_euler(G, critere='cout')
        dessiner_graphe_sur_carte_avec_chemin(chemin_euler, DG, chemin_image_carte, poids_total=poids_total, titre=f"{'parcours' if semieuler else 'circuit'} Euler", critere='cout', direction=True, export_path="chemin_euler.jpg")

    # BONUS 6: Glouton (manuel - not finished) 

    # BONUS 7a - imposer une ville d'escale
    ville_depart="Brest"
    ville_arrivee="Bordeaux"
    ville_escale="Nice"

    print(f"BONUS 7a: Chemin le moins cher entre {ville_depart} et {ville_arrivee} en passant par {ville_escale}")
    chemin_cout, poids_total = meilleur_chemin_escale(graphe=G, ville_depart=ville_depart, ville_escale=ville_escale, ville_arrivee=ville_arrivee, critere='cout', debug=False)
    dessiner_graphe_sur_carte_avec_chemin(chemin_cout, G, chemin_image_carte, titre=f'chemin le moins cher en passant par {ville_escale}', critere='cout', poids_total=poids_total, export_path="chemin_cout_escale.jpg")

    # BONUS 7b - chemin le moins cher SANS routes départementales SANS quelques villes
    ville_depart="Rouen"
    ville_arrivee="Toulouse"
    villes_exclues=["Paris","Marseille"]

    print(f"BONUS 7b: Chemin le moins cher entre {ville_depart} et {ville_arrivee} SANS routes départementales et SANS passer par {villes_exclues}")
    G_filtre = filtre_graphe(G,type_a_exclure='d',ville_a_exclure=villes_exclues)
    dessiner_graphe_sur_carte(G_filtre, chemin_image_carte, titre="Carte sans routes départementales", show_cout=True, export_path="carte_sans_dept_avec_cout_exclure_villes.jpg")
    chemin_cout_sans_d, poids_total = meilleur_chemin(graphe=G_filtre, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='cout')
    dessiner_graphe_sur_carte_avec_chemin(chemin_cout_sans_d, G_filtre, chemin_image_carte, titre='chemin le moins cher', critere='cout', poids_total=poids_total, contrainte=f"sans routes départementales et sans {villes_exclues}", export_path="chemin_cout_no_d_no_ville.jpg")




    
    


    
    


    
