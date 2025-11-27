import csv
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys
import heapq # Utilisé pour la file de priorité de Dijkstra (le standard de l'implémentation efficace de Dijkstra)

# Augmenter la limite de récursion pour l'affichage de grands graphes si nécessaire
sys.setrecursionlimit(5000)

print("Bibliothèques importées avec succès.")

# ---
# 1. Fonction de chargement CSV (non modifiée)
# ---
def charger_csv_en_matrice(nom_fichier):
    """
    Charge un fichier CSV (avec délimiteur ';') et le retourne sous forme de 
    liste de listes (matrice), incluant l'en-tête.
    """
    matrice = []
    try:
        with open(nom_fichier, mode='r', encoding='utf-8') as f:
            lecteur = csv.reader(f, delimiter=';')
            for ligne in lecteur:
                if ligne:
                    matrice.append(ligne)
        print(f"Fichier {nom_fichier} chargé. {len(matrice) - 1} lignes de données trouvées.")
        return matrice
    except FileNotFoundError:
        print(f"ERREUR: Le fichier {nom_fichier} n'a pas été trouvé.")
        return None
    except Exception as e:
        print(f"ERREUR lors de la lecture de {nom_fichier}: {e}")
        return None

# ---
# 2. Fonction de création du graphe (non modifiée)
# ---
def creer_graphe(data_liaison):
    """
    Crée un graphe NetworkX à partir de la matrice de données des liaisons.
    """
    if not data_liaison or len(data_liaison) < 2:
        print("ERREUR: Données de liaison invalides ou vides.")
        return None

    G = nx.Graph()
    header = data_liaison[0]
    
    try:
        idx_v1 = header.index('Ville1')
        idx_v2 = header.index('ville2')
        idx_type = header.index('type')
        idx_duree = header.index('duree')
        idx_cout = header.index('cout')
    except ValueError as e:
        print(f"ERREUR: Colonne manquante dans TP2_liaison {e}")
        return None

    for ligne in data_liaison[1:]:
        if len(ligne) > max(idx_v1, idx_v2, idx_type, idx_duree, idx_cout):
            try:
                ville1 = ligne[idx_v1]
                ville2 = ligne[idx_v2]
                type_liaison = ligne[idx_type]
                duree = float(ligne[idx_duree])
                cout = float(ligne[idx_cout])
                
                G.add_edge(ville1, ville2, type=type_liaison, duree=duree, cout=cout)
            except ValueError as e:
                print(f"AVERTISSEMENT: Ligne ignorée (problème de conversion): {ligne} - {e}")
            except Exception as e:
                print(f"AVERTISSEMENT: Erreur sur ligne {ligne} - {e}")
    
    print(f"Graphe créé: {G.number_of_nodes()} villes, {G.number_of_edges()} liaisons.")
    return G

# ---
# Fonction utilitaire pour charger les positions (non modifiée)
# ---
def charger_positions(data_position):
    """
    Crée un dictionnaire de positions {ville: (x, y)} à partir 
    de la matrice de données des positions.
    """
    if not data_position or len(data_position) < 2:
        return {}

    positions = {}
    header = data_position[0]
    
    try:
        idx_ville = header.index('ville')
        idx_x = header.index('posX')
        idx_y = header.index('posY')
    except ValueError:
        return {}
        
    for ligne in data_position[1:]:
        if len(ligne) > max(idx_ville, idx_x, idx_y):
            try:
                ville = ligne[idx_ville]
                x = float(ligne[idx_x])
                y = float(ligne[idx_y])
                positions[ville] = (x, y)
            except ValueError:
                pass 
    
    print(f"Positions chargées pour {len(positions)} villes.")
    return positions

# ---
# 3. Fonction d'affichage du graphe initial (Modification pour la taille)
# ---
def dessiner_graphe_sur_carte(graphe, positions, chemin_image_carte):
    """
    Dessine le graphe sur l'image de la carte de France.
    """
    if graphe is None or not positions:
        print("Affichage impossible: graphe ou positions invalides.")
        return

    try:
        img = mpimg.imread(chemin_image_carte)
    except FileNotFoundError:
        print(f"ERREUR: Fichier image '{chemin_image_carte}' non trouvé.")
        return
    
    # Appliquer la dimension de figure en (60,15) comme exigé par le TP
    plt.rcParams["figure.figsize"] = (60, 15)
    
    # Créer la figure avec une taille d'affichage plus gérable et DPI élevé 
    # pour un meilleur rendu sans être trop grand à l'écran.
    # Note: On conserve le ratio 4:1 pour la cohérence visuelle.
    fig, ax = plt.subplots(figsize=(20, 5), dpi=100) 
    
    ax.imshow(img)
    
    couleurs_aretes = []
    for u, v in graphe.edges():
        if graphe.edges[u, v]['type'] == 'a':
            couleurs_aretes.append('red')
        else:
            couleurs_aretes.append('green')
            
    nx.draw_networkx(
        graphe,
        pos=positions,
        ax=ax,
        node_size=100,
        node_color='blue',
        font_size=10,
        font_color='black',
        edge_color=couleurs_aretes,
        width=2,
        with_labels=True # Afficher les noms de villes
    )
    
    print("Affichage du graphe sur la carte...")
    plt.title("Graphe des liaisons sur la carte de France")
    plt.show()


# =============================================================================
# --- FONCTION CLE : ALGORITHME DE DIJKSTRA MANUEL 
# =============================================================================

def dijkstra_path(graphe, ville_depart, ville_arrivee, poids_critere):
    """
    Implémentation manuelle de l'algorithme de Dijkstra pour trouver le chemin
    le plus court entre la ville de depart et la ville d'arrivee selon le 'poids_critere'.

    Retourne: La liste des villes formant le chemin, ou un message d'erreur.
    """
    if ville_depart not in graphe or ville_arrivee not in graphe:
        return "Une des villes n'a pas été trouvée dans le graphe."

    # 1. Initialisation
    distances = {ville: float('inf') for ville in graphe.nodes}
    predecesseurs = {ville: None for ville in graphe.nodes}
    distances[ville_depart] = 0
    
    # File de priorité: (distance_actuelle, ville_actuelle)
    pq = [(0, ville_depart)] 

    # 2. Boucle principale de Dijkstra
    while pq:
        # Extraire la ville non visitée avec la plus petite distance
        dist_actuelle, u = heapq.heappop(pq)

        # Si nous avons déjà trouvé un chemin plus court pour 'u', ignorer cette entrée
        if dist_actuelle > distances[u]:
            continue
        
        # Si la destination est atteinte
        if u == ville_arrivee:
            break

        # 3. Relaxation des arêtes
        for v in graphe.neighbors(u):
            # Récupérer le poids de l'arête (critère durée ou coût)
            poids = graphe.get_edge_data(u, v).get(poids_critere, float('inf'))
            
            nouvelle_distance = dist_actuelle + poids

            # Si on trouve un chemin plus court vers v
            if nouvelle_distance < distances[v]:
                distances[v] = nouvelle_distance
                predecesseurs[v] = u
                heapq.heappush(pq, (nouvelle_distance, v))

    # 4. Reconstruction du chemin
    if distances[ville_arrivee] == float('inf'):
        return f"Aucun chemin n'existe entre {ville_depart} et {ville_arrivee}."

    chemin = []
    ville_courante = ville_arrivee
    while ville_courante is not None:
        chemin.append(ville_courante)
        ville_courante = predecesseurs[ville_courante]
    
    # Le chemin est reconstruit à l'envers, il faut l'inverser
    return chemin[::-1]

# =============================================================================
# --- Fonctions Utilisant Dijkstra
# =============================================================================

# --- Nouvelle fonction utilitaire pour le parcours en profondeur (DFS) ---
def parcours_dfs(graphe, depart):
    """
    Effectue un parcours en profondeur (DFS) à partir du sommet de départ
    et retourne l'ensemble des sommets accessibles (visités).
    """
    visites = set()
    pile = [depart] # Utilisation d'une pile (liste) pour le DFS

    while pile:
        sommet_actuel = pile.pop()
        
        if sommet_actuel not in visites:
            visites.add(sommet_actuel)
            
            # Ajouter les voisins non visités à la pile
            for voisin in graphe.neighbors(sommet_actuel):
                if voisin not in visites:
                    pile.append(voisin)
                    
    return visites


# 1. Connexité (RECODÉE SANS nx.is_connected) ---
def est_connexe(graphe):
    """
    Vérifie la connexité en utilisant le Parcours en Profondeur (DFS).
    Retourne Vrai si le graphe est connexe, Faux sinon.
    """
    # Cas d'un graphe vide ou sans sommets
    if graphe.number_of_nodes() == 0:
        return True # Un graphe vide est souvent considéré comme connexe
    
    # 1. Choisir un sommet de départ arbitraire (le premier dans la liste des nœuds)
    sommet_depart = list(graphe.nodes())[0]
    
    # 2. Effectuer le parcours pour trouver les sommets accessibles
    sommets_visites = parcours_dfs(graphe, sommet_depart)
    
    # 3. Vérifier si tous les sommets ont été visités
    if len(sommets_visites) == graphe.number_of_nodes():
        return True
    else:
        return False


# 2. Meilleur chemin (durée)
def meilleur_chemin_duree(graphe, ville_depart, ville_arrivee):
    """Retourne le chemin le plus court en termes de 'duree' via Dijkstra."""
    return dijkstra_path(graphe, ville_depart, ville_arrivee, 'duree')

# 3. Meilleur chemin (coût)
def meilleur_chemin_cout(graphe, ville_depart, ville_arrivee):
    """Retourne le chemin le moins cher en termes de 'cout' via Dijkstra."""
    return dijkstra_path(graphe, ville_depart, ville_arrivee, 'cout')

# ---
# Fonctions pour les chemins avec contraintes (le filtre reste le même)
# ---
def creer_graphe_filtre(graphe_original, type_a_exclure):
    """
    Crée une copie du graphe en excluant les arêtes d'un certain type ('a' ou 'd').
    """
    G_filtre = nx.Graph()
    G_filtre.add_nodes_from(graphe_original.nodes())
    
    for u, v, data in graphe_original.edges(data=True):
        if data['type'] != type_a_exclure:
            G_filtre.add_edge(u, v, **data)
    return G_filtre

# 4. Meilleur chemin (durée, sans autoroutes)
def meilleur_chemin_duree_sans_autoroute(graphe, ville_depart, ville_arrivee):
    """Retourne le chemin le plus court (durée) sans arêtes de type 'a'."""
    G_filtre = creer_graphe_filtre(graphe, 'a')
    return dijkstra_path(G_filtre, ville_depart, ville_arrivee, 'duree')

# 5. Meilleur chemin (coût, sans départementales)
def meilleur_chemin_cout_sans_departementale(graphe, ville_depart, ville_arrivee):
    """Retourne le chemin le moins cher (coût) sans arêtes de type 'd'."""
    G_filtre = creer_graphe_filtre(graphe, 'd')
    return dijkstra_path(G_filtre, ville_depart, ville_arrivee, 'cout')


# 6. Affichage du chemin surligné (Modification pour la taille)
def afficher_chemin_sur_carte(chemin, graphe, positions, chemin_image_carte):
    """
    Affiche la carte avec le chemin spécifié en couleur, 
    calcule et affiche la durée et le coût total du trajet.
    """
    
    # Vérifier si le chemin est valide (doit être une liste de villes)
    if not isinstance(chemin, list) or len(chemin) < 2:
        print(f"Impossible d'afficher le chemin: {chemin}")
        return

    # --- Calcul du coût et de la durée ---
    total_duree = 0
    total_cout = 0
    aretes_chemin = []
    
    try:
        for i in range(len(chemin) - 1):
            u = chemin[i]
            v = chemin[i+1]
            # Utilise get_edge_data pour être compatible avec les graphes filtrés
            data = graphe.get_edge_data(u, v)
            
            total_duree += data['duree']
            total_cout += data['cout']
            aretes_chemin.append((u, v))
            
        print(f"--- Itinéraire: {' -> '.join(chemin)} ---")
        print(f"     Durée totale estimée: {total_duree:.1f} minutes")
        print(f"     Coût total estimé: {total_cout:.2f} €")
        
    except Exception as e:
        print(f"ERREUR lors du calcul du coût du chemin {chemin}: {e}")
        return

    # --- Affichage sur la carte ---
    try:
        img = mpimg.imread(chemin_image_carte)
    except FileNotFoundError:
        print(f"ERREUR: Fichier image '{chemin_image_carte}' non trouvé.")
        return
    
    plt.rcParams["figure.figsize"] = (60, 15)
    # Créer la figure avec une taille d'affichage plus gérable et DPI élevé 
    fig, ax = plt.subplots(figsize=(20, 5), dpi=100) 
    ax.imshow(img)
    
    # Dessiner tous les nœuds et labels
    nx.draw_networkx_nodes(graphe, pos=positions, ax=ax, node_size=100, node_color='gray')
    nx.draw_networkx_labels(graphe, pos=positions, ax=ax, font_size=10, font_color='black')
    
    # Dessiner toutes les arêtes (fond) en gris clair
    nx.draw_networkx_edges(graphe, pos=positions, ax=ax, edge_color='lightgray', width=1)
    
    # Surligner les arêtes du chemin
    nx.draw_networkx_edges(
        graphe,
        pos=positions,
        ax=ax,
        edgelist=aretes_chemin,
        edge_color='blue',
        width=4
    )
    
    # Surligner les nœuds du chemin
    nx.draw_networkx_nodes(
        graphe,
        pos=positions,
        ax=ax,
        nodelist=chemin,
        node_size=150,
        node_color='red'
    )
    
    plt.title(f"Chemin: {chemin[0]} -> {chemin[-1]}")
    plt.show()


# =============================================================================
# --- BLOC D'EXÉCUTION PRINCIPAL (Exemple d'utilisation - non modifié) ---
# =============================================================================
if __name__ == "__main__":
    
    # Noms des fichiers (assurez-vous qu'ils sont dans le même répertoire)
    # NOTE: Ces noms de fichiers sont donnés à titre d'exemple et doivent correspondre aux fichiers réels.
    fichier_liaisons = 'TP2_liaison.csv' # Le nom exact du fichier donné dans le TP
    fichier_positions = 'TP2_position.csv' # Le nom exact du fichier donné dans le TP
    fichier_carte = 'carte.jpg'

    print("--- Étape 1: Chargement des données ---")
    data_liaisons = charger_csv_en_matrice(fichier_liaisons)
    data_positions = charger_csv_en_matrice(fichier_positions)

    if data_liaisons and data_positions:
        
        print("\n--- Étape 2: Création du graphe ---")
        G = creer_graphe(data_liaisons)
        pos = charger_positions(data_positions)

        if G and pos:
            # --- Étape 3: Afficher le graphe initial ---
            print("\n--- Étape 3: Affichage du graphe complet ---")
            dessiner_graphe_sur_carte(G, pos, fichier_carte)
            
            # --- Tests des fonctions supplémentaires ---
            
            # 1. Connexité
            print(f"\n--- Test 1: Connexité ---")
            print(f"Le graphe est-il connexe ? {est_connexe(G)}")
            
            # Définir des villes de test
            ville_depart = "Brest"
            ville_arrivee = "Nice"
            
            # 2. Meilleur chemin (durée)
            print(f"\n--- Test 2: Meilleur chemin (durée) de {ville_depart} à {ville_arrivee} ---")
            chemin_duree = meilleur_chemin_duree(G, ville_depart, ville_arrivee)
            afficher_chemin_sur_carte(chemin_duree, G, pos, fichier_carte)
            
            # 3. Meilleur chemin (coût)
            print(f"\n--- Test 3: Meilleur chemin (coût) de {ville_depart} à {ville_arrivee} ---")
            chemin_cout = meilleur_chemin_cout(G, ville_depart, ville_arrivee)
            afficher_chemin_sur_carte(chemin_cout, G, pos, fichier_carte)
            
            # 4. Meilleur chemin (durée, sans autoroute)
            print(f"\n--- Test 4: Meilleur chemin (durée, SANS autoroutes) de {ville_depart} à {ville_arrivee} ---")
            chemin_sans_a = meilleur_chemin_duree_sans_autoroute(G, ville_depart, ville_arrivee)
            afficher_chemin_sur_carte(chemin_sans_a, G, pos, fichier_carte)
            
            # 5. Meilleur chemin (coût, sans départementale)
            print(f"\n--- Test 5: Meilleur chemin (coût, SANS départementales) de {ville_depart} à {ville_arrivee} ---")
            chemin_sans_d = meilleur_chemin_cout_sans_departementale(G, ville_depart, ville_arrivee)
            afficher_chemin_sur_carte(chemin_sans_d, G, pos, fichier_carte)

        else:
            print("Erreur lors de la création du graphe ou du chargement des positions. Arrêt.")
    else:
        print("Erreur lors du chargement des fichiers CSV. Arrêt.")