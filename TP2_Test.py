import csv
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys # Utilisé pour gérer les valeurs max

# Augmenter la limite de récursion pour l'affichage de grands graphes si nécessaire
sys.setrecursionlimit(5000)

print("Bibliothèques importées avec succès.")

# ---
# 1. Ecrire une fonction qui prend en entrée un fichier (format .csv) et qui 
#    retourne les informations sous forme de matrice (array).
# ---
def charger_csv_en_matrice(nom_fichier):
    """
    Charge un fichier CSV (avec délimiteur ';') et le retourne sous forme de 
    liste de listes (matrice), incluant l'en-tête.
    """
    matrice = []
    try:
        with open(nom_fichier, mode='r', encoding='utf-8') as f:
            # Utiliser csv.reader avec le délimiteur point-virgule
            lecteur = csv.reader(f, delimiter=';')
            for ligne in lecteur:
                # Filtrer les lignes vides qui pourraient résulter de la fin du fichier
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
# 2. Ecrire une fonction qui prend en entrée le tableau contenant les 
#    informations du fichier TP2-liaison.csv, et qui retourne le graphe correspondant.
# ---
def creer_graphe(data_liaison):
    """
    Crée un graphe NetworkX à partir de la matrice de données des liaisons.
    Les arêtes auront des attributs 'type', 'duree' et 'cout'.
    """
    if not data_liaison or len(data_liaison) < 2:
        print("ERREUR: Données de liaison invalides ou vides.")
        return None

    G = nx.Graph()
    header = data_liaison[0]
    
    # Trouver les index des colonnes (plus robuste que de supposer l'ordre)
    try:
        idx_v1 = header.index('Ville1')
        idx_v2 = header.index('ville2')
        idx_type = header.index('type')
        idx_duree = header.index('duree')
        idx_cout = header.index('cout')
    except ValueError as e:
        print(f"ERREUR: Colonne manquante dans TP2_liaison.csv - {e}")
        return None

    # Parcourir les lignes de données (ignorer l'en-tête)
    for ligne in data_liaison[1:]:
        # Assurer que la ligne a suffisamment de colonnes
        if len(ligne) > max(idx_v1, idx_v2, idx_type, idx_duree, idx_cout):
            try:
                ville1 = ligne[idx_v1]
                ville2 = ligne[idx_v2]
                type_liaison = ligne[idx_type]
                # Convertir durée et coût en nombres (float)
                duree = float(ligne[idx_duree])
                cout = float(ligne[idx_cout]) # Le CSV utilise '.' comme séparateur
                
                # Ajouter l'arête avec ses attributs (poids)
                G.add_edge(ville1, ville2, type=type_liaison, duree=duree, cout=cout)
            except ValueError as e:
                print(f"AVERTISSEMENT: Ligne ignorée (problème de conversion): {ligne} - {e}")
            except Exception as e:
                print(f"AVERTISSEMENT: Erreur sur ligne {ligne} - {e}")
    
    print(f"Graphe créé: {G.number_of_nodes()} villes, {G.number_of_edges()} liaisons.")
    # 
    return G

# ---
# Fonction utilitaire pour charger les positions (nécessaire pour l'étape 3)
# ---
def charger_positions(data_position):
    """
    Crée un dictionnaire de positions {ville: (x, y)} à partir 
    de la matrice de données des positions.
    """
    if not data_position or len(data_position) < 2:
        print("ERREUR: Données de position invalides ou vides.")
        return {}

    positions = {}
    header = data_position[0]
    
    try:
        idx_ville = header.index('ville')
        idx_x = header.index('posX')
        idx_y = header.index('posY')
    except ValueError as e:
        print(f"ERREUR: Colonne manquante dans TP2_position.csv - {e}")
        return {}
        
    for ligne in data_position[1:]:
        if len(ligne) > max(idx_ville, idx_x, idx_y):
            try:
                ville = ligne[idx_ville]
                x = float(ligne[idx_x])
                y = float(ligne[idx_y])
                positions[ville] = (x, y)
            except ValueError as e:
                print(f"AVERTISSEMENT: Ligne de position ignorée: {ligne} - {e}")
    
    print(f"Positions chargées pour {len(positions)} villes.")
    return positions

# ---
# 3. Ecrire une fonction qui affiche le graphe sur la carte de France.
#    Note: La consigne demande (probablement par erreur) "le tableau... TP2-liaison.csv".
#    Cette fonction a logiquement besoin des *positions* (TP2-position.csv)
#    et du graphe (créé à l'étape 2).
# ---
def dessiner_graphe_sur_carte(graphe, positions, chemin_image_carte):
    """
    Dessine le graphe sur l'image de la carte de France.
    Autoroutes (type 'a') en rouge, Départementales (type 'd') en vert.
    """
    if graphe is None:
        print("Affichage impossible: le graphe est None.")
        return
    if not positions:
        print("Affichage impossible: les positions sont vides.")
        return

    try:
        img = mpimg.imread(chemin_image_carte)
    except FileNotFoundError:
        print(f"ERREUR: Fichier image '{chemin_image_carte}' non trouvé.")
        return
    
    # Appliquer la dimension de figure en (60,15).
    plt.rcParams["figure.figsize"] = (60, 15)
    
    fig, ax = plt.subplots()
    
    # Afficher l'image de la carte
    ax.imshow(img)
    
    # Déterminer les couleurs des arêtes
    couleurs_aretes = []
    for u, v in graphe.edges():
        if graphe.edges[u, v]['type'] == 'a':
            couleurs_aretes.append('red')
        else:
            couleurs_aretes.append('green') # Supposant 'd' ou autre
            
    # Dessiner le graphe par-dessus l'image
    nx.draw_networkx(
        graphe,
        pos=positions,      # Dictionnaire des positions {ville: (x, y)}
        ax=ax,              # Dessiner sur l'axe de la carte
        node_size=100,
        node_color='blue',
        font_size=10,
        font_color='black',
        edge_color=couleurs_aretes,
        width=2
    )
    
    print("Affichage du graphe sur la carte...")
    plt.title("Graphe des liaisons sur la carte de France")
    plt.show()


# ---
# Fonctions pour trouver les meilleurs chemins
# ---

# 1. Connexité
def est_connexe(graphe):
    """Retourne Vrai si le graphe est connexe, Faux sinon."""
    return nx.is_connected(graphe)

# 2. Meilleur chemin (durée)
def meilleur_chemin_duree(graphe, ville_depart, ville_arrivee):
    """Retourne le chemin le plus court en termes de 'duree'."""
    try:
        return nx.shortest_path(graphe, source=ville_depart, target=ville_arrivee, weight='duree')
    except nx.NetworkXNoPath:
        return f"Aucun chemin n'existe entre {ville_depart} et {ville_arrivee}."
    except nx.NodeNotFound:
        return "Une des villes n'a pas été trouvée dans le graphe."

# 3. Meilleur chemin (coût)
def meilleur_chemin_cout(graphe, ville_depart, ville_arrivee):
    """Retourne le chemin le moins cher en termes de 'cout'."""
    try:
        return nx.shortest_path(graphe, source=ville_depart, target=ville_arrivee, weight='cout')
    except nx.NetworkXNoPath:
        return f"Aucun chemin n'existe entre {ville_depart} et {ville_arrivee}."
    except nx.NodeNotFound:
        return "Une des villes n'a pas été trouvée dans le graphe."

# ---
# Fonctions pour les chemins avec contraintes
# ---
def creer_graphe_filtre(graphe_original, type_a_exclure):
    """
    Crée une copie du graphe en excluant les arêtes d'un certain type ('a' ou 'd').
    """
    G_filtre = nx.Graph()
    # Ajouter tous les nœuds
    G_filtre.add_nodes_from(graphe_original.nodes())
    
    # N'ajouter que les arêtes qui NE SONT PAS du type à exclure
    for u, v, data in graphe_original.edges(data=True):
        if data['type'] != type_a_exclure:
            G_filtre.add_edge(u, v, **data)
    return G_filtre

# 4. Meilleur chemin (durée, sans autoroutes)
def meilleur_chemin_duree_sans_autoroute(graphe, ville_depart, ville_arrivee):
    """Retourne le chemin le plus court (durée) sans arêtes de type 'a'."""
    G_filtre = creer_graphe_filtre(graphe, 'a')
    try:
        # Vérifier si les villes existent toujours dans le graphe filtré
        if not G_filtre.has_node(ville_depart) or not G_filtre.has_node(ville_arrivee):
             return "Villes de départ ou d'arrivée non accessibles sans autoroutes."
        return nx.shortest_path(G_filtre, source=ville_depart, target=ville_arrivee, weight='duree')
    except nx.NetworkXNoPath:
        return f"Aucun chemin sans autoroute n'existe entre {ville_depart} et {ville_arrivee}."

# 5. Meilleur chemin (coût, sans départementales)
def meilleur_chemin_cout_sans_departementale(graphe, ville_depart, ville_arrivee):
    """Retourne le chemin le moins cher (coût) sans arêtes de type 'd'."""
    G_filtre = creer_graphe_filtre(graphe, 'd')
    try:
        if not G_filtre.has_node(ville_depart) or not G_filtre.has_node(ville_arrivee):
             return "Villes de départ ou d'arrivée non accessibles sans départementales."
        return nx.shortest_path(G_filtre, source=ville_depart, target=ville_arrivee, weight='cout')
    except nx.NetworkXNoPath:
        return f"Aucun chemin sans départementale n'existe entre {ville_depart} et {ville_arrivee}."


# 6. Ecrire une fonction... qui affiche le chemin en couleur sur la carte, 
#    ainsi que la durée et le côut total du trajet.
# ---
def afficher_chemin_sur_carte(chemin, graphe, positions, chemin_image_carte):
    """
    Affiche la carte avec TOUT le graphe en gris clair, 
    et surligne le 'chemin' spécifié en bleu.
    Calcule et affiche également la durée et le coût total du chemin.
    """
    
    # Vérifier si le chemin est valide
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
            data = graphe.get_edge_data(u, v)
            
            total_duree += data['duree']
            total_cout += data['cout']
            aretes_chemin.append((u, v))
            
        print(f"--- Itinéraire: {' -> '.join(chemin)} ---")
        print(f"    Durée totale estimée: {total_duree} minutes")
        print(f"    Coût total estimé: {total_cout:.2f} €")
        
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
    fig, ax = plt.subplots()
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
        edgelist=aretes_chemin, # Ne dessiner que celles-ci
        edge_color='blue',
        width=4
    )
    
    # Surligner les nœuds du chemin
    nx.draw_networkx_nodes(
        graphe,
        pos=positions,
        ax=ax,
        nodelist=chemin, # Ne dessiner que ceux-ci
        node_size=150,
        node_color='red'
    )
    
    plt.title(f"Chemin: {chemin[0]} -> {chemin[-1]}")
    plt.show()


# =============================================================================
# --- BLOC D'EXÉCUTION PRINCIPAL (Exemple d'utilisation) ---
# =============================================================================
if __name__ == "__main__":
    
    # Noms des fichiers (assurez-vous qu'ils sont dans le même répertoire)
    fichier_liaisons = 'TP2_liaison.csv'
    fichier_positions = 'TP2_position.csv'
    fichier_carte = 'carte.jpg'

    # --- Étape 1: Charger les données ---
    print("--- Étape 1: Chargement des données ---")
    data_liaisons = charger_csv_en_matrice(fichier_liaisons)
    data_positions = charger_csv_en_matrice(fichier_positions)

    # Vérifier que les chargements ont réussi
    if data_liaisons and data_positions:
        
        # --- Étape 2: Créer le graphe ---
        print("\n--- Étape 2: Création du graphe ---")
        G = creer_graphe(data_liaisons)
        
        # Charger les positions
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
            ville_depart = "Lille"
            ville_arrivee = "Marseille"
            
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
            # Note: Le CSV fourni ne semble contenir que des autoroutes ('a').
            # Cette fonction trouvera donc le même chemin que la 3.
            print(f"\n--- Test 5: Meilleur chemin (coût, SANS départementales) de {ville_depart} à {ville_arrivee} ---")
            chemin_sans_d = meilleur_chemin_cout_sans_departementale(G, ville_depart, ville_arrivee)
            afficher_chemin_sur_carte(chemin_sans_d, G, pos, fichier_carte)

            # Test avec d'autres villes
            ville_depart_2 = "Brest"
            ville_arrivee_2 = "Strasbourg"
            
            print(f"\n--- Test 6: Meilleur chemin (coût) de {ville_depart_2} à {ville_arrivee_2} ---")
            chemin_cout_2 = meilleur_chemin_cout(G, ville_depart_2, ville_arrivee_2)
            afficher_chemin_sur_carte(chemin_cout_2, G, pos, fichier_carte)

        else:
            print("Erreur lors de la création du graphe ou du chargement des positions. Arrêt.")
    else:
        print("Erreur lors du chargement des fichiers CSV. Arrêt.")