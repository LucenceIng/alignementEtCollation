#!usr/bin/env python
# -*- coding: utf-8 -*-


from fonctions_alignment import *

### alignement

## les fichiers doivent avoir un premier niveau de structuration et de correspondance, avec un @xml:id et un @corresp
# les fichiers sauf le témoin de base doivent avoir un @corresp qui soit l'@xml:id du témoin de base

"""
#on parse les documents qui doivent être en TEI
Ao_plein = etree.parse("Ao.xml")
Ez_plein = etree.parse("Ez.xml")
#C_plein = etree.parse("C.xml")

# création d'une liste vide
listeAMatcher = []
# on applique la méhode prodDiv à nos variables obtenues ci-dessus
# premier argument : un identifiant
# second : le XML/TEI parsé
# troisième : le niveau sur lequel on veut aligner. Ce niveau doit avoir un @xml:id et un @corresp. Le @corresp des témoins autres que celui de base doivent renvoyer uniquement à l'identifiant du témoin de base
Ao = XMLtoJsonParDiv("Ao", Ao_plein,"div").prodDiv()
Ez = XMLtoJsonParDiv("Ez", Ez_plein,"div").prodDiv()
#C = XMLtoJsonParDiv("C", C_plein, "div").prodDiv()

# on ajoute à la liste les témoins qui doivent matcher (pas le témoin de base)
listeAMatcher.append(Ez)
#listeAMatcher.append(C)

# pour chacun des témoins dans les témoins à aligner avec le témoin de base
for x in listeAMatcher:
    # appliquer la fonction boucleMatch
    boucleMatch(Ao,x)
"""

# avec la fonction 


# on donne le dossier dans lequel se trouve les documents TEI à aligner
dossier = 'textes'
# on donne le sigle du témoin (== aussi nom du fichier sans extension)
temBase = 'Ao'
            
## boucle Match appplique sur le dossier renseigné dans dossier le match
## il faut préciser le témoin de base (en chaîne de caractères) et le niveau au sein duquel on veut obtenir des unités plus petites
boucleMatchDossier(dossier,temBase,'div')