import csv

def charger_csv_en_matrice(nom_fichier):
    matrice = []
    with open(nom_fichier, mode='r', encoding='utf-8') as f:
        lecteur = csv.reader(f, delimiter=';')
        for ligne in lecteur:
            if ligne:
                matrice.append(ligne)
    return matrice

if __name__ == "__main__":
    matrice = charger_csv_en_matrice("TP2_position.csv")
    print(matrice)
