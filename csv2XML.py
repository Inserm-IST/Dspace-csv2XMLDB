"""
Script qui permet, pour un fichier csv contenant les métadonnées de plusieurs fichiers, d'obtenir un fichier DublinCore
par document.
Auteur:Juliette Janes
Date:26/10/2021
Contexte: Mise en ligne de fonds d'Archives sur iPubli
"""

import pandas as pd
from lxml import etree as ET
import click
import os
import shutil

def creation_balise_double(case, root_dc, el, qual, num_item, lang=False, conditionnel=False):
    """
    Fonction qui, pour une cellule csv fournie, vérifie si plusieurs informations sont contenus et ajoute en fonction
    les éléments dans des balises correspondantes dans l'arbre xml
    :param case: cellule du csv
    :type case: str
    :param root_dc: arbre xml créé
    :type root_dc: elementtree
    :param el: valeur de l'attribut élément de la balise
    :type el: str
    :param qual: valeur de l'attribut qualifier de la balise
    :type qual: str
    :param lang: valeur de l'attribut language de la balise
    :type lang: str
    :param conditionnel: booléen pour savoir si
    :return: arbre XML avec le sujet ajouté
    """
    if isinstance(case, float) and not conditionnel:
        print("Cette ligne n'a pas toutes ses métadonnées obligatoires de complétées.")
        with open('anomalies.txt', 'a') as f:
            f.write("ligne: " + str(num_item) + " métadonnée manquante: " + el+"\n")
    else:
        if "||" in case:
            # Si oui on divise le contenu de la cellule en une liste de sujets
            liste_case = case.split("||")
            for indiv in liste_case:
                # création d'un élément dans l'arbre XML sous la forme suivante:
                # <dcvalue element="element fourni" qualifier="qualifier fourni"/>
                balise_dc = ET.SubElement(root_dc, "dcvalue", qualifier=qual, element=el)
                if lang:
                    # la langue est mentionné, ajout d'un troisième attribut sous la forme language="langue fournie"
                    balise_dc.attrib["language"] = lang
                # ajout du contenu de la cellule traitée dans la balise comme texte.
                balise_dc.text = indiv
        else:
            # Si non on créé une unique balise sujet dans laquelle on ajoute tout le contenu de la cellule subject du csv
            balise_dc = ET.SubElement(root_dc, "dcvalue", qualifier=qual, element=el)
            if lang:
                balise_dc.attrib["language"] = lang
            balise_dc.text = case

    return root_dc


def creation_balise_simple(case, root_dc, el, qual, num_item, lang=False, conditionnel = False):
    """
    fonction qui, pour une cellule csv fournie ajoute le texte contenu dans la balise correspondante dans l'arbre xml
    :param case: cellule du csv
    :type case: str
    :param root_dc: arbre xml créé
    :type root_dc: elementtree
    :param el: valeur de l'attribut élément de la balise
    :type el: str
    :param qual: valeur de l'attribut qualifier de la balise
    :type qual: str
    :param lang: valeur de l'attribut language de la balise
    :type lang: str
    :return: arbre XML avec le sujet ajouté
    """
    # création d'un élément dans l'arbre XML sous la forme suivante:
    # <dcvalue element="element fourni" qualifier="qualifier fourni"/>
    balise_dc = ET.SubElement(root_dc, "dcvalue", element=el, qualifier=qual)
    if lang:
        # la langue est mentionné, ajout d'un troisième attribut sous la forme language="langue fournie"
        balise_dc.attrib["language"]=lang
    # ajout du contenu de la cellule traitée dans la balise comme texte.
    if isinstance(case, float) and not conditionnel:
        print("Cette ligne n'a pas toutes ses métadonnées obligatoires de complétées.")
        with open('anomalies.txt', 'a') as f:
            f.write("ligne: "+str(num_item)+" métadonnée manquante: " + el +"\n" )
    else:
        balise_dc.text = case

    return root_dc


def creation_balise_simple_if(colonne, MD_ligne, root_dc, el, qual, lang=False):
    """
    fonction qui, pour un nom de colonne fourni, teste l'existance et celle-ci dans le csv. Si existante, la fonction
    creation balise simple est utilisée et ajoute l'élément dans l'arbre XML
    :param colonne: nom de la colonne à tester
    :type colonne: str
    :param root_dc: arbre xml créé
    :type root_dc: elementtree
    :param el: valeur de l'attribut élément de la balise
    :type el: str
    :param qual: valeur de l'attribut qualifier de la balise
    :type qual: str
    :param lang: valeur de l'attribut language de la balise
    :type lang: str
    :return: arbre XML avec le sujet ajouté
    """
    try:
        num = MD_ligne['item']
        # si la colonne existe, on applique la fonction creation_balise_simple sur les différents éléments récupérés
        # afin d'ajouter son contenu dans l'arbre XML
        root_dc = creation_balise_simple(MD_ligne[colonne], root_dc, el, qual, num,
                                            lang, conditionnel = True)
    except (KeyError, TypeError) as e:
        # sinon, il y a une erreur, que l'on passe
        pass
    return root_dc


def creation_balise_double_if(colonne, MD_ligne, root_dc, el, qual, lang=False):
    """
    fonction qui, pour un nom de colonne fourni, teste l'existance et celle-ci dans le csv. Si existante, la fonction
    creation balise double est utilisée et ajoute l'élément dans l'arbre XML
    :param colonne: nom de la colonne à tester
    :type colonne: str
    :param root_dc: arbre xml créé
    :type root_dc: elementtree
    :param el: valeur de l'attribut élément de la balise
    :type el: str
    :param qual: valeur de l'attribut qualifier de la balise
    :type qual: str
    :param lang: valeur de l'attribut language de la balise
    :type lang: str
    :return: arbre XML avec le sujet ajouté
    """
    try:
        num = MD_ligne['item']
        # si la colonne existe, on applique la fonction creation_balise_double sur les différents éléments récupérés
        # afin d'ajouter son contenu dans l'arbre XML
        root_dc = creation_balise_double(MD_ligne[colonne], root_dc, el, qual, num,
                                            lang, conditionnel=True)
    except (KeyError, TypeError) as e:
        # sinon, il y a une erreur que l'on passe
        pass
    return root_dc


def create_xml(MD_ligne, root_dc):
    """
    Fonction qui, à partir d'une ligne csv donnée, créé l'arbre xml correspondant
    :param MD_ligne: ligne du csv
    :return: Structure XML
    """
    # création de la racine xml
    root_dc = ET.Element("dublin_core", page=str(MD_ligne["item"]))
    # appel de la fonction creation_balise_simple pour l'élément titre qui ajoute le contenu de la case titre pour le fichier
    # dans l'arbre xml entre balise
    root_dc = creation_balise_simple(MD_ligne["Titre"], root_dc, "title", "none",MD_ligne["item"], "fr")
    # appel de la fonction creation_balise_simple_if pour l'élément titre alternatif qui vérifie l'existence de cette colonne
    # et, auquel cas, ajoute le contenu de la case dans l'arbre xml
    root_dc = creation_balise_simple_if("Titre alternatif", MD_ligne, root_dc, "title", "alternative", "fr")
    # appel de la fonction creation_balise_double qui pour l'élément auteur, divise les différents éléments entre || qui la composent
    # et créé plusieurs balise auteur contenant chacun de ces textes
    root_dc = creation_balise_double(MD_ligne["Auteur"], root_dc, "contributor", "author",MD_ligne["item"])
    # appel de la fonction création_balise_double_if qui pour l'élément affiliation, vérifie son existence et, le cas
    # échéant, divise les éléments entre || qui la compose et créé une balise affiliation par texte.
    root_dc = creation_balise_double_if("Conseillers", MD_ligne, root_dc, "contributor", "advisor", "fr")
    root_dc = creation_balise_double_if("Affiliation", MD_ligne, root_dc, "contributor", "affiliation")
    # par la suite, appel d'une de ces quatre fonctions en fonction de l'utilisation (optionnelle ou non, multiple ou non)
    # de chaque élément
    root_dc = creation_balise_double(MD_ligne["Description (fr)"], root_dc, "description", "none", MD_ligne["item"],"fr")
    root_dc = creation_balise_double_if("Description (en)",MD_ligne, root_dc, "description", "none", "en")
    root_dc = creation_balise_double_if("Table des matières",MD_ligne, root_dc, "description", "tableofcontents",
                                         "fr")
    root_dc = creation_balise_simple_if("Description extrait",MD_ligne, root_dc, "description", "abstract",
                                         "fr")
    root_dc = creation_balise_simple(MD_ligne["Editeur (direction)"], root_dc, "contributor", "editor",MD_ligne["item"], "fr")
    root_dc = creation_balise_simple(MD_ligne['Editeur ("Publisher")'], root_dc, "publisher", "none",MD_ligne["item"], "fr")
    root_dc = creation_balise_simple(str(MD_ligne["Date de publication"]), root_dc, "date", "issued",MD_ligne["item"], "fr")
    root_dc = creation_balise_simple_if("Date de numérisation",MD_ligne, root_dc, "date", "created",
                                             "fr")
    root_dc = creation_balise_double(MD_ligne["Type"], root_dc, "type", "none", MD_ligne["item"],"fr")
    root_dc = creation_balise_simple_if("Type (en)",MD_ligne, root_dc, "type", "none", "en")
    root_dc = creation_balise_simple(MD_ligne["Langage"], root_dc, "language", "iso",MD_ligne["item"], "fr")
    root_dc = creation_balise_simple_if("Relation (isPartOf)", MD_ligne, root_dc, "relation", "ispartof", "fr")
    root_dc = creation_balise_simple_if("Relation (isPartOfSerie)", MD_ligne, root_dc, "relation", "ispartofserie", "fr")
    root_dc = creation_balise_simple(MD_ligne["Droit"], root_dc, "rights", "none",MD_ligne["item"])
    root_dc = creation_balise_simple_if("Gestionnaire des droits", MD_ligne, root_dc, "rightsHolder","none", "fr")
    root_dc = creation_balise_simple_if("Source", MD_ligne, root_dc, "source","none", "fr")
    root_dc = creation_balise_simple_if("Citation information", MD_ligne, root_dc, "identifier", "citation", "fr")
    root_dc = creation_balise_double_if("Mot-clé (MeSH)", MD_ligne, root_dc, "subject", "mesh","fr")
    root_dc = creation_balise_double_if("Mot-clé (fr/en)", MD_ligne, root_dc, "subject","none","fr")
    root_dc = creation_balise_simple_if(str("Durée"), MD_ligne, root_dc, "format", "extent")

    return root_dc




def create_lots(MD_fichier, thematique):
    """Fonction qui créé des lots pour import dans iPubli par la suite
    ATTENTION: pour utiliser cette fonction, il faut mettre l'intégralité des documents à ajouter dans les lots dans
    un dossier media (de même pour les sommaires dans un dossier sommaire) en renommant chaque fichier en ajoutant le
    numéro d'item correspondant de telle façon: NOM_FICHIER_numitem.pdf (si pdf)"""
    # récupération du numéro du fichier traité dans la colonne item
    num_item = str(int(MD_fichier['item']))
    # si l'utilisateur a coché l'option thématique qui organise les lots en sous catégorie
    if thematique:
        # récupération le nom de la thématique auquel appartient le fichier
        nom_thematique = MD_fichier['Thématique']
        # création du chemin selon la structure thématique/item+numéro/
        nom_dossier = nom_thematique+"/item_"+num_item+"/"
    else:
        # création du chemin selon la structure item+numero/
        nom_dossier = "item_"+num_item+"/"
    # vérification de l'existance du chemin. Si les dossiers n'existent pas, création.
    doc_existe = os.path.exists(nom_dossier)
    if not doc_existe:
        os.makedirs(nom_dossier)
    # renvoi du chemin obtenu
    return nom_dossier




@click.command()
@click.argument("fichier", type=str)
@click.option("-l", "--lots","creationlots",is_flag=True, default=False, help="creation lots pour import iPubli")
@click.option("-t", "--them", "thematique", is_flag=True, default=False, help="si création de lots avec dossier thématique")
def csv2db(fichier, creationlots, thematique):
    # creation du fichier anomalies
    with open('anomalies.txt', 'w') as f:
        f.write("Métadonnées obligatoires manquantes: \n")
    # lecture du csv et stockage du contenu dans l'objet df
    df = pd.read_csv(fichier)
    # Récupération du nombre de fichiers décrits dans le csv
    length_df = int(len(df.index))
    # initialisation des objets utilisés dans la boucle suivante
    n = 0
    root_dc=0
    # Pour chaque ligne du csv (soit les métadonnées d'un fichier) réalisation des opérations suivantes
    while n != length_df:
        # récupération de la ligne de métadonnées dans le csv
        MD_fichier = df.loc[n]
        # Information à l'utilisateur du traitement du fichier
        print("Traitement du fichier n° " + str(int(MD_fichier["item"])))
        # création de l'arbre XML qui va contenir les métadonnées du fichier
        root_dc = create_xml(MD_fichier,root_dc)
        # Si l'option dispatchant les xml créés dans les fichiers lots a été sélectionnés, réalisation des opérations
        # suivantes
        if creationlots:
            # création du chemin vers lequel le fichier xml doit être généré
            nom_dossier = create_lots(MD_fichier, thematique)
            # création du nom du fichier xml
            nom = nom_dossier+"dublin_core.xml"
        else:
            # sinon, création du nom du fichier xml au niveau du programme avec le numéro d'item dans le nom
            nom= "dublin_core_"+str(int(MD_fichier['item']))+".xml"
        # incrémentation
        n += 1
        # impression de l'arbre XMl dans le fichier correspondant
        ET.ElementTree(root_dc).write(nom, encoding="UTF-8", xml_declaration=True)
        # Information à l'utilisateur que le fichier a bien été traité
        print("Fichier n° " + str(int(MD_fichier["item"])) + " traité et disponible sous la forme "+ nom)


if __name__ == "__main__":
    csv2db()
