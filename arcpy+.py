def Join_attribute (couche, ListeChamp):
    '''
    Entrée : 
    couche : str du chemin de la couche shp qui subira la jointure
    ListeChamp : liste de dictionnaire qui permet de connaitre les champs à joindre, il doit se présenter sous la forme : 
    ListeChamp = [
        {"name": "Name1", "rename": "Rename1", "type": "DOUBLE", "length": "100", "champ_commun_1": "id_1", "champ_commun_2": "id_2",  "file": file},...]  
            file : table ou couche à joindre
            champ_commun_1 : champ présent dans la couche de base qui permet de joindre
            champ_commun_2 : champ présent dans la couche de jointure qui permet de joindre
    
    fonction pour jointure attributaire (plus compliqué que la fonction de base arcpy)
    '''
    
    # Ajout des champs
    for champ in ListeChamp:
        testChamp = arcpy.ListFields(couche, champ['rename'])
        if len(testChamp) == 0:
            arcpy.AddField_management(couche, champ['rename'], champ['type'], champ['length'])
            print "Ajout du champ " + champ['rename']
        else:
            print "Le champ %s existe déjà" %champ['rename']
    
    # Parcours des champs pour chaque jointure attributaire    
    for champ in ListeChamp:
        #incrémentation de la vue pour chaque fichier à joindre
        print ("jointure attributaire avec " + champ['file'])
        vue_shp = "vue_" + nom_couche(champ['file']) + "_" + nom_couche(couche)
        # jointure de chaque champ
        try :
            arcpy.AddIndex_management(couche, champ['champ_commun_1'], champ['champ_commun_2'])
        except:
            print ("index deja cree")
        try:
            arcpy.AddIndex_management(champ['file'], champ['champ_commun_1'], champ['champ_commun_2'])
        except:
            print ("index deja cree")
        
        if arcpy.Exists(vue_shp) == False:
            print ("Vue : " + vue_shp)
            arcpy.MakeTableView_management(couche, vue_shp)
        print ("arcpy.AddJoin_management(" + nom_couche(vue_shp) + ", " + champ['champ_commun_1'] + ", " + champ['file'] + ", " + champ['champ_commun_2'] + ")")
        arcpy.AddJoin_management(vue_shp, champ['champ_commun_1'], champ['file'], champ['champ_commun_2'], "KEEP_ALL")
        print ("arcpy.CalculateField_management( " + vue_shp + ", " + nom_couche(couche) + "." + champ['rename'] + ", [" + nom_couche(champ['file']) + "." + champ['name'] + "], VB)")        
        arcpy.CalculateField_management(vue_shp, nom_couche(couche) + "." + champ['rename'], "[" + nom_couche(champ['file']) + "." + champ['name'] + "]", "VB")
        time.sleep(0.1)
        arcpy.RemoveJoin_management(vue_shp)
    
def renseignerchampSQL (couche_shp, list_champ, list_type, list_requeteSQL, list_reponses):
    '''
    Entrée :
    couche_shp : chaine de caractère de la couche où l'on va rajouter les champs
    list_champ : liste des champs à rajouter
    list_type : liste des types des champs, on vérifiera si le nombre de type correspond au nombre de champ
    
    Sortie :
    Aucune les champs sont juste mis à jour    
    '''
    # l'utilisateur veut ajouter quelques champs
    print ("%s") %list_champ
    print ("%s") %list_type
    
    if len(list_champ) == len(list_type):
        for compteur in range(len(list_champ)):
            fieldList = arcpy.ListFields(couche_shp, list_champ[compteur])
            if len(fieldList) == 0:
                arcpy.AddField_management(couche_shp, list_champ[compteur], list_type[compteur])
            print ("creation du champ %s" %list_champ[compteur])
            time.sleep(0.1)
            
        for compteur in range(len(list_champ)):
            maclause = list_requeteSQL[compteur]
            with arcpy.da.UpdateCursor(couche_shp, list_champ[compteur], "%s" %maclause ) as cur1:
                for row in cur1 :
                    row[0] =  list_reponses[compteur]
                    cur1.updateRow(row)
                print (list_champ[compteur] + " calcule !")
                del cur1
            
            maclause = list_champ[compteur] + " IS NULL"
            with arcpy.da.UpdateCursor(couche_shp, list_champ[compteur], "%s" %maclause ) as cur2:
                for row in cur2 :
                    row[0] =  "False"
                    cur2.updateRow(row)
                print ("correction des valeurs NULL en False")
                del cur2
    elif (len(list_champ) > len(list_type)):
        print ("Il manque des types de champs")
    else:
        print ("il y a trop de type de champs")
        
        
def surfaceParEntite(couche_shp, couche_shp_dissolve, champs_group, ListChamp):
    '''
    Entrée :
    couche_shp : chaine de caractère de la couche où l'on va calculer les surfaces
    champs_group : Champs de regroupement pour la fonction
    list_champ : liste des champs dont on veut les stats de surfaces
    
    Sortie :
    Aucune les champs sont juste mis à jour
    '''

    mavar_stat = ""
    for champ in ListChamp:
        fieldList = arcpy.ListFields(couche_shp, champ)
        if len(fieldList) == 0:
            print ("Le champ " + champ + " n'existe pas")
        else:
            mavar_stat += champ + " SUM; "

    print ("%s") %mavar_stat
    
    # On règle les problèmes de toppologie avant de faire le dissolve
    arcpy.management.RepairGeometry(couche_shp, "KEEP_NULL")

    # dissolve
    if arcpy.Exists(couche_shp_dissolve):
        arcpy.Delete_management(couche_shp_dissolve, "FeatureClass")
    arcpy.management.Dissolve(couche_shp, couche_shp_dissolve, champs_group, mavar_stat)

   
    print ("Dissolve " + couche_shp_dissolve + " ok !")

def Null2Zero(couche_shp, listChamp):
    '''
    couche_shp : couche avec des champs nuls
    listChamp : ensemble des champs qui ont des valeurs nulles
    
    La fonction met à jour des champs nuls pour les remplir avec des valeurs '0'
    '''

    for champ in listChamp:
        fieldList = arcpy.ListFields(couche_shp, champ)
        if len(fieldList) == 0:
            print ("Le champ " + champ + " n'existe pas")
        else :
            maclause = champ + " is NULL"
            print ("%s") %maclause
            print ("%s") %champ
            with arcpy.da.UpdateCursor(couche_shp, "%s" %champ, "%s" %maclause) as cur2:
                for row in cur2 :
                    row[0] =  0
                    cur2.updateRow(row)
                print (champ + " calcule !")
                del cur2

def COSetCES (couche_shp, champ_surf_bati, champ_surf_emprise, champ_surf_parc):
    '''
    couche_shp : Couche du calcul où l'on va calculer le COS
    champ_surf_bati : champ de surface des batiments pour le COS
    champ_surf_emprise : champ de surface de l'emprise du batiment
    champ_surf_parc : champ de surface de la parcelle
    '''
    ListChamp = [champ_surf_bati, champ_surf_emprise, champ_surf_parc]
   
    for champ in ListChamp:
        nvchamp = champ + "_NUM"
        fieldList = arcpy.ListFields(couche_shp, nvchamp)
        if len(fieldList) == 0:
            arcpy.AddField_management(couche_shp, nvchamp, "DOUBLE", "18", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(couche_shp, nvchamp, "[%s]" %champ, "VB", "")
        print ("creation du champ %s" %nvchamp)
    
    fieldList = arcpy.ListFields(couche_shp, "COS" )
    if len(fieldList) == 0:
        arcpy.AddField_management(couche_shp, "COS", "DOUBLE", "18", "2", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(couche_shp, "COS", "0", "VB", "")
    
    #Calcul du COS    
    maclause = champ_surf_bati + " > 0 and " + champ_surf_parc + " > 0 "
    fields = ["COS", champ_surf_bati, champ_surf_parc]
    with arcpy.da.UpdateCursor(couche_shp, fields, maclause) as curCOS:
  	for row in curCOS:
  	    row[0] =  row[1]  /  row[2]
            curCOS.updateRow(row)
    print ("calc COS")
    del curCOS
    
       
    maclause = "COS IS NULL"
    fields = ["COS"]
    with arcpy.da.UpdateCursor(couche_shp, fields, maclause) as curCOSisNULL:
  	for row in curCOSisNULL :
  	    row[0] =  0
            curCOSisNULL.updateRow(row)
    print ("COS is null")
    del curCOSisNULL
    
    #Calcul du CES    
    maclause = champ_surf_emprise + " > 0 and " + champ_surf_parc + " > 0 "
    fields = ["COS", champ_surf_emprise, champ_surf_parc]
    with arcpy.da.UpdateCursor(couche_shp, fields, maclause) as curCES:
  	for row in curCES:
  	    row[0] =  row[1]  /  row[2]
            curCOS.updateRow(row)
    print ("calc CES")
    del curCES
    
       
    maclause = "CES IS NULL"
    fields = ["CES"]
    with arcpy.da.UpdateCursor(couche_shp, fields, maclause) as curCESisNULL:
  	for row in curCESisNULL :
  	    row[0] =  0
            curCESisNULL.updateRow(row)
    print ("CES is null")
    del curCESisNULL

def scoring_interne(couche_shp, champ, maclause, score):
    '''
    couche_shp : Couche du calcul où l'on va calculer le score
    champ : champ de scoring
    maclause : clause du score appliquable
    score : score à appliquer
    '''
    
    # test de la nature de la valeur à rentrer
    nature = 'TEXT'
    longueur = 100
    if type(score) == int:
        nature == 'LONG'
        longueur = 100
    if type(score) == float:
        nature == 'DOUBLE'
        longueur = 8000
    
    testChamp = arcpy.ListFields(couche_shp, champ)
    if len(testChamp) == 0:
        arcpy.AddField_management(couche_shp, champ, nature, longueur)

    print ("%s") %champ
    print ("%s") %maclause
    print ("arcpy.da.UpdateCursor(%s, %s, %s)" %(nom_couche(couche_shp), champ, maclause))
    with arcpy.da.UpdateCursor(couche_shp, champ, maclause) as cur1:
        for row in cur1:
            row[0] = score
            cur1.updateRow(row)
        print ("Calcul du champ " + champ)
        del cur1    
        
def nettoyageCouche (couche_shp, champ_gardee):
    '''
    Entrée :
    couche_shp : couche dont on veut supprimmer les champs
    champ_gardee : listes des champs que l'on veut garder (il est inutile de rajouter les champs obligatoire, ils sont rajouter par la fonction
    
    Sortie : 
    Aucune, la fonction modifie la couche existante
    '''
    champ_gardee += ["OBJECTID", "Surface", "Shape_Area", "Shape_Length", "Shape"]
    champ_suppr = []

    fieldList = arcpy.ListFields(couche_shp)
    for field in fieldList:
        if field.name not in champ_gardee:
            champ_suppr.append(field.name)

    print "On garde les champs : " + str(champ_gardee)
    print "On supprime les champs : " + str(champ_suppr)
    arcpy.DeleteField_management(couche_shp, champ_suppr)
    print "suppression de champs intermédiaires"
    
