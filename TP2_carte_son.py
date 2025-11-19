import csv

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

if __name__ == "__main__":
    matrice = charger_csv_en_matrice("TP2_position.csv")
    print(matrice)

    sommets = charger_sommets(matrice)
    print(sommets)

    
