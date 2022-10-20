# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# fonctions utiles pour la geomatique

# Import arcpy module

import arcpy
import time
# ---------------------------------------------------------------------------
# fonctions purement python
# ---------------------------------------------------------------------------

def nom_couche (couche):
    '''
    Entree :
    chemin de couche (str)
    
    Sortie :
    nom_couche (str)
    
    fonction qui construit le nom de la couche a partir du chemin de la couche    
    '''
    # déclaration variables
    positionSlash = 0
    compteur = 0

    # On parcours le mot
    for compteur in range(len(couche)):
        # Si on trouve un slash, on incremente le compteur de slash
        if couche[compteur] == "\\":
            positionSlash = compteur
            compteur += 1
        else :
        # sinon, on continue dans le mot
            compteur += 1
    if couche[-4:] == ".shp":
        return couche[positionSlash + 1:-4]
    else :
        return couche[positionSlash + 1:]
    
def racine (couche):
    '''
    Entree :
    chemin de couche (str)
    
    Sortie :
    racine (str)
    
    fonction qui construit le nom de la couche a partir du chemin de la couche, si la couche est dans une GDB, la racine s'arrêtera à la GDB (elle ne rentrera pas dans les jeux de données)
    '''
    gdb = False

    for compteur in range(len(couche)):
        if couche[compteur:compteur + 4].lower() == ".gdb":
            gdb = True

    if gdb:
        compteur = 0
        while couche[compteur] != ".":
            compteur += 1
    
        return couche[:compteur + 4]
    else :
        positionSlash = 0
        compteur = 0
        # On parcours le mot
        for compteur in range(len(couche)):
            # Si on trouve un slash, on incremente le compteur de slash
            if couche[compteur] == "\\":
                positionSlash = compteur
                compteur += 1
            else :
                # sinon, on continue dans le mot
                compteur += 1
        return couche[:positionSlash]
   
def joursEcoules (date):
    '''
    Entrée :
    Date = chaine de caractère (string) sous la forme JJ/MM/AAAA

    Sortie :
    delta.days = nombre de jour écoulés depuis la date entrée
    '''
    aujourdhui = datetime.date(int(datetime.datetime.today().strftime('%Y')), int(datetime.datetime.today().strftime('%m')), int(datetime.datetime.today().strftime('%d')))
    date = datetime.date(int(date[-4:]), int(date[-7:-5]), int(date[0:-8]))
    delta = aujourdhui - date
    return delta.days
