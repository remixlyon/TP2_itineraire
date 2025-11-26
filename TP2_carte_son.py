import csv
import heapq
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Fonction pour charger CSV en matrice
def charger_csv_en_matrice(nom_fichier) -> list:
    matrice = []
    with open(nom_fichier, mode='r', encoding='utf-8') as f:
        lecteur = csv.reader(f, delimiter=';')
        for ligne in lecteur:
            if ligne:
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

    # add_nodes prend en input dict (sommet:[x,y], ...)
    for ville, pos in sommets.items():
        G.add_node(ville, pos=pos)

    # add_edges_from prend en input une liste (sommet1, sommet2, {data1,data2 ...})
    G.add_edges_from(liaisons)
    return G

# Fonction pour dessiner le graphe sur le JPG
def dessiner_graphe_sur_carte(graphe, chemin_image_carte, titre, show_cout=False, show_duree=False, export_path=None):
    # lire l'image
    img = mpimg.imread(chemin_image_carte)

    # size canvas = 10x10
    plt.rcParams["figure.figsize"] = (10, 10)

    # ax = plot zone
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

    pos = nx.get_node_attributes(graphe, 'pos')

    # utilisant nx, dessiner le graphe
    nx.draw_networkx(
        graphe, # réseau des liaisons
        pos=pos, # sommets
        ax=ax, # plot
        edge_color=couleurs_aretes,
        font_size=10,
        width=2
    )

    if show_cout == True:
        edge_labels = {(u, v): f"{d['cout']}€" for u, v, d in graphe.edges(data=True)}
        nx.draw_networkx_edge_labels(
            graphe,
            pos=pos,
            edge_labels=edge_labels,
            font_size=5,
            ax=ax
        )

    if show_duree == True:
        edge_labels = {(u, v): f"{d['duree']}m" for u, v, d in graphe.edges(data=True)}
        nx.draw_networkx_edge_labels(
            graphe,
            pos=pos,
            edge_labels=edge_labels,
            font_size=5,
            ax=ax
        )

    # afficher la zone (avec le plot ax)
    plt.title(f"{titre}")

    if export_path is not None:
        plt.savefig(export_path, format='jpg', dpi=300)

    plt.show()

# Fonction pour dessiner le graphe sur le JPG et tracer le chemin
def dessiner_graphe_sur_carte_avec_chemin(chemin: list, graphe, chemin_image_carte, critere, poids_total, titre, contrainte = "", direction=False, export_path=None):
    # redessiner la carte
    img = mpimg.imread(chemin_image_carte)
    plt.rcParams["figure.figsize"] = (10, 10)
    fig, ax = plt.subplots()
    ax.imshow(img,cmap="gray")
   
    pos = nx.get_node_attributes(graphe, 'pos')

    # utilisant nx, dessiner le graphe, couleur grise pour highlight plus tard
    nx.draw_networkx(
        graphe,
        pos=pos,
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
            pos=pos,
            ax=ax,
            nodelist=chemin[1:-1],
            node_color='red'
        )

        # Surligner en blue les extrémités du chemin
        nx.draw_networkx_nodes(
            graphe,
            pos=pos,
            ax=ax,
            nodelist=[chemin[0],chemin[-1]],
            node_color='blue'
        )

    
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
            pos=pos,
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
                pos=pos,
                edge_labels=edge_labels,
                font_size=5,
                ax=ax
            )
            plt.title(f"{chemin[0]} -> {chemin[-1]} {contrainte}: {titre}. Cout total = {round(poids_total,2)}€")
        else:
            edge_labels = {(u, v): f"{d['duree']}m" for u, v, d in graphe.edges(data=True)}
            nx.draw_networkx_edge_labels(
                graphe,
                pos=pos,
                edge_labels=edge_labels,
                font_size=5,
                ax=ax
            )
            plt.title(f"{chemin[0]} -> {chemin[-1]} {contrainte}: {titre}. Duree totale = {int(poids_total // 60)}h {int(poids_total % 60)} minutes")

    elif poids_total==0 and len(chemin)==1:
        plt.title(f"{chemin[0]}")
    else:
        plt.title(f"{chemin[0]} -> {chemin[-1]} {contrainte}: pas de route")


    if export_path is not None:
        plt.savefig(export_path, format='jpg', dpi=300)
    plt.show()

# Fonction pour trouver le meilleur chemin (remplaçant manuel de nx.shortest_path)
def meilleur_chemin(graphe, ville_depart, ville_arrivee, critere, debug=False) -> tuple[list, float]:

    # Etape 0: vérifier si les villes données sont valides
    if ville_depart not in graphe:
        msg = f"{ville_depart} n'est pas présente dans la carte"
        print(msg)        
        return [msg],0
    if ville_arrivee not in graphe:
        msg = f"{ville_depart} n'est pas présente dans la carte"
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
    # initier un dict pour noter les meilleurs sommet-1
    predecesseurs = {ville: None for ville in graphe.nodes}

    # 2. Boucle principale de Dijkstra
    # File de priorité: (distance_actuelle, ville_actuelle)
    pq = [(0, ville_depart)] 
    if debug: print(f'>> START: départ de {ville_depart}') 
    while pq:
        # Extraire le sommet non visité avec la plus petite distance
        dist_nouvelle, u = heapq.heappop(pq)
        if debug: print(f'>> Explorer les voisins de {u} ({dist_nouvelle}): {list(graphe.neighbors(u))}') 

        # Si nous avons déjà trouvé un chemin plus court pour 'u', ignorer cette entrée et reprendre la boucle WHILE
        if dist_nouvelle > distances[u]:
            if debug: print(f'>>    On a déjà une distance plus petite pour {u} (actuelle {distances[u]}; nouvelle {dist_nouvelle})') 
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
            if debug: print(f'>>    Nouvelle distance de {v} = {nouvelle_distance}') 

            # 2b. Mettre à jour le poid du voisin v si on trouve un chemin plus court vers lui
            if nouvelle_distance < distances[v]:
                distances[v] = nouvelle_distance
                if debug: print(f'>>    Meilleure distance trouvée pour {v} = {nouvelle_distance}') 

                predecesseurs[v] = u
                if debug: print(f'>>    Mettre à jour le chemin vers {v} en passant par {u}') 
                heapq.heappush(pq, (nouvelle_distance, v))

    # 3. Reconstruction du chemin
    meilleur_chemin = []
    if distances[ville_arrivee] == float('inf'):
        meilleur_chemin = [ville_depart,ville_arrivee]
        poids_total = 0
        print(f"    Aucun chemin n'existe entre {ville_depart} et {ville_arrivee}.")
        return meilleur_chemin, poids_total

    ville_courante = ville_arrivee
    while ville_courante is not None:
        meilleur_chemin.append(ville_courante)
        ville_courante = predecesseurs[ville_courante]
    
    # Le chemin est reconstruit à l'envers, il faut l'inverser
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

        if ville_depart in sommets_vu:
            continue

        print(f"Exploration à partir de: {ville_depart}")

        # DFS
        stack = [ville_depart]
        continent = set([ville_depart])
        sommets_vu.add(ville_depart)

        while stack:
            node = stack.pop()

            for neighbor in graphe.neighbors(node):
                if neighbor not in sommets_vu:
                    sommets_vu.add(neighbor)
                    continent.add(neighbor)
                    stack.append(neighbor)

                    # Show progress
                    print(f"{neighbor} est connectée")

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

# BONUS2: lister tous les bons chemins
def meilleur_chemin_all(graphe, ville_depart, ville_arrivee, critere) -> list:
    try:
        meilleur_chemin_all = nx.all_shortest_paths(graphe, source=ville_depart, target=ville_arrivee, weight=critere)
    except nx.NetworkXNoPath:
        print(f"Aucun chemin n'existe entre {ville_depart} et {ville_arrivee}.")
        return [ville_depart,ville_arrivee]
    return meilleur_chemin_all

# BONUS3: lister tous les chemins
def all_paths_with_costs(graphe, ville_depart, ville_arrivee, critere="cout"):
    paths = list(nx.all_simple_paths(graphe, ville_depart, ville_arrivee))
    results = []

    for path in paths:
        cost = 0
        for u, v in zip(path[:-1], path[1:]):
            cost += graphe[u][v][critere]   # sum the cost attribute

        results.append((path, cost))

    return results

# BONUS4: Kruskal MST
def find_mst(graphe, critere="cout"):
    T = nx.minimum_spanning_tree(graphe, weight=critere)
    
    return T































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
    
    # dessiner_graphe_sur_carte(G, sommets, chemin_image_carte, "Carte Initiale")
    # dessiner_graphe_sur_carte(G, sommets, chemin_image_carte, "Carte Initiale", show_cout=True, export_path="carte_initiale.jpg")
    

    # =================================================================================================
    
    # Q1
    est_connexe, continents = connexe_manuel(G)
    if est_connexe:
        connexe = "est connexe"
    else: connexe = "n'est pas connexe"
    print()
    print(f"Q1: Le graphe {connexe}")

    print(f"Le graphe contient {len(continents)} groupe(s) connexe(s)")
    for continent in continents:
        print(f"    Continent ({continents.index(continent)+1}) contient {len(continent)} villes(s):")
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

    print(f"Q2: Chemin le plus court entre : {ville_depart} et {ville_arrivee}")
    chemin_duree, poids_total = meilleur_chemin(graphe=G, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='duree', debug=True)
    dessiner_graphe_sur_carte_avec_chemin(chemin_duree, G, chemin_image_carte, titre='chemin le plus court', critere='duree', poids_total=poids_total)



    # Q3 - chemin le moins cher
    ville_depart="Paris"
    ville_arrivee="Marseille"
    print(f"Q3: Chemin le moins cher entre : {ville_depart} et {ville_arrivee}")
    chemin_cout, poids_total = meilleur_chemin(graphe=G, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='cout')
    dessiner_graphe_sur_carte_avec_chemin(chemin_cout, G, chemin_image_carte, titre='chemin le moins cher', critere='cout', poids_total=poids_total)



    # Q4 - chemin le plus court SANS autoroutes
    ville_depart="Paris"
    ville_arrivee="Havre"
    
    print(f"Q4: Chemin le plus court SANS autoroutes entre : {ville_depart} et {ville_arrivee}")
    G_filtre = filtre_graphe(G,'a')
    dessiner_graphe_sur_carte(G_filtre, chemin_image_carte, titre="Carte sans autoroutes", show_duree=True, export_path="carte_sans_autoroute_avec_duree.jpg")
    chemin_duree_sans_a, poids_total = meilleur_chemin(graphe=G_filtre, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='duree')
    dessiner_graphe_sur_carte_avec_chemin(chemin_duree_sans_a, G_filtre, chemin_image_carte, titre='chemin le plus court', critere='duree', poids_total=poids_total, contrainte="sans autoroutes")

    # Q5 - chemin le moins cher SANS routes départementales
    ville_depart="Rouen"
    ville_arrivee="Nice"

    print(f"Q5: Chemin le moins cher SANS routes départementales entre : {ville_depart} et {ville_arrivee}")
    G_filtre = filtre_graphe(G,'d')
    dessiner_graphe_sur_carte(G_filtre, chemin_image_carte, titre="Carte sans routes départementales", show_cout=True, export_path="carte_sans_dept_avec_cout.jpg")
    chemin_cout_sans_d, poids_total = meilleur_chemin(graphe=G_filtre, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='cout')
    dessiner_graphe_sur_carte_avec_chemin(chemin_cout_sans_d, G_filtre, chemin_image_carte, titre='chemin le moins cher', critere='cout', poids_total=poids_total, contrainte="sans routes départementales")

    # Q5-bonus - chemin le moins cher SANS routes départementales SANS quelques villes
    ville_depart="Rouen"
    ville_arrivee="Toulouse"
    villes_exclues=["Paris","Marseille"]

    print(f"Q5-bonus: Chemin le moins cher SANS routes départementales et sans passer par {villes_exclues} entre : {ville_depart} et {ville_arrivee}")
    G_filtre = filtre_graphe(G,type_a_exclure='d',ville_a_exclure=villes_exclues)
    dessiner_graphe_sur_carte(G_filtre, chemin_image_carte, titre="Carte sans routes départementales", show_cout=True, export_path="carte_sans_dept_avec_cout_exclure_villes.jpg")
    chemin_cout_sans_d, poids_total = meilleur_chemin(graphe=G_filtre, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='cout')
    dessiner_graphe_sur_carte_avec_chemin(chemin_cout_sans_d, G_filtre, chemin_image_carte, titre='chemin le moins cher', critere='cout', poids_total=poids_total, contrainte="sans routes départementales")





















    # # ==============================================================================================

    # # BONUS1 - afficher le chemin le plus rapide et le chemin le moins cher sur le même graphe
    # ville_depart="Brest"
    # ville_arrivee="Marseille"

    # print(f"BONUS1: Chemin le moins cher vs. le plus rapide entre : {ville_depart} et {ville_arrivee}")
    # chemin_cout = meilleur_chemin(graphe=G, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='cout')
    # chemin_duree = meilleur_chemin(graphe=G, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='duree')
    
    # chemin_duree_inverse = list(reversed(chemin_duree))
    # if len(chemin_duree_inverse) > 2:
    #     chemin_duree_inverse = chemin_duree_inverse[1:]
    # chemin_total = chemin_cout + chemin_duree_inverse
    
    # dessiner_graphe_sur_carte_avec_chemin(chemin_total, G, sommets, chemin_image_carte, titre='time vs. money', critere='cout')


    # # BONUS2 - afficher tous les "shortest paths"
    # ville_depart="Brest"
    # ville_arrivee="Nice"

    # meilleur_chemin_all = list(meilleur_chemin_all(graphe=G, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='cout'))
    # print(meilleur_chemin_all)




    # # BONUS3 - afficher tous les chemins et leur coût. Filtre le graphe avant de lancer l'algo car trop de résultats sinon
    # ville_depart="Brest"
    # ville_arrivee="Nice"

    # # G_filtre = filtre_graphe(G,'a')
    # # dessiner_graphe_sur_carte(G_filtre, sommets, chemin_image_carte, "Carte sans autoroutes", show_duree=True, export_path="carte_sans_autoroute_avec_duree.jpg")

    # G_filtre = filtre_graphe(G,'d')
    # dessiner_graphe_sur_carte(G_filtre, sommets, chemin_image_carte, "Carte sans routes départementales", show_cout=True, export_path="carte_sans_dept_avec_cout.jpg")

    # result = all_paths_with_costs(graphe=G_filtre, ville_depart=ville_depart, ville_arrivee=ville_arrivee, critere='cout')
    # # Afficher les 5 meilleurs chemins
    # result_sorted = sorted(result, key=lambda x: x[1])
    # for path in result_sorted[0:5]:
    #     print(path)


    # # BONUS4 - afficher l'arbre couvrant poid minimum (MST)
    # T_cout = find_mst(G,'cout')
    # dessiner_graphe_sur_carte(T_cout, sommets, chemin_image_carte, "MST coût", export_path="mst_cout.jpg")

    # T_duree = find_mst(G,'duree')
    # dessiner_graphe_sur_carte(T_duree, sommets, chemin_image_carte, "MST durée", export_path="mst_duree.jpg")

    

    # # BONUS 5a - checker si le graphe est semi-euler
    # sommets_impairs = [x for x in G.nodes() if G.degree(x) % 2 == 1]
    # for sommet in sommets_impairs:
    #     print(f"{sommet} - {G.degree(sommet)}")
        
    # euler = nx.is_eulerian(G)
    # print(f"Graphe dispose d'un cicuit euler ? {euler}")

    # semieuler = nx.is_semieulerian(G)
    # print(f"Graphe dispose d'un parcours euler ? {semieuler}")

    # if semieuler:
    #     aretes_euler_path = list(nx.eulerian_path(G))

    #     # Create directed graph and copy node positions
    #     DG = nx.DiGraph()
    #     DG.add_nodes_from(G.nodes(data=True))

    #     # Add edges along the Euler path and assign the order
    #     for order, (u, v) in enumerate(aretes_euler_path, start=1):
    #         # Copy edge attributes from the original undirected graph
    #         attr = G[u][v].copy()
    #         attr['cout'] = order  # overwrite cout with Euler order
    #         DG.add_edge(u, v, **attr)

    #     nodes_euler_path = [aretes_euler_path[0][0]] + [v for u, v in aretes_euler_path]
    #     dessiner_graphe_sur_carte_avec_chemin(nodes_euler_path, DG, sommets, chemin_image_carte, titre='parcours Euler', critere='cout', direction=True, export_path="euler_path.jpg")

    # # BONUS 5b - checker si le graphe est euler (supprimer en plus Clermont - Dijon & Chermont - Marseille)
    # sommets_impairs = [x for x in G.nodes() if G.degree(x) % 2 == 1]
    # for sommet in sommets_impairs:
    #     print(f"{sommet} - {G.degree(sommet)}")
        
    # euler = nx.is_eulerian(G)
    # print(f"Graphe dispose d'un cicuit euler ? {euler}")

    # semieuler = nx.is_semieulerian(G)
    # print(f"Graphe dispose d'un parcours euler ? {semieuler}")

    # if euler:
    #     aretes_euler_circuit = list(nx.eulerian_path(G, source="Paris"))

    #     # Create directed graph and copy node positions
    #     DG = nx.DiGraph()
    #     DG.add_nodes_from(G.nodes(data=True))

    #     # Add edges along the Euler path and assign the order
    #     for order, (u, v) in enumerate(aretes_euler_circuit, start=1):
    #         # Copy edge attributes from the original undirected graph
    #         attr = G[u][v].copy()
    #         attr['cout'] = order  # overwrite cout with Euler order
    #         DG.add_edge(u, v, **attr)

    #     nodes_euler_circuit = [aretes_euler_circuit[0][0]] + [v for u, v in aretes_euler_circuit]
    #     dessiner_graphe_sur_carte_avec_chemin(nodes_euler_circuit, DG, sommets, chemin_image_carte, titre='circuit Euler', critere='cout', direction=True, export_path="euler_circuit.jpg")

    



    
    


    
    


    
