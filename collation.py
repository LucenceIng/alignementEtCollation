#!usr/bin/env python
# -*- coding: utf-8 -*-


import collatex
from collatex.edit_graph_aligner import *
from collatex.core_classes import *
from collatex.near_matching import *
from fonctions_collation import *


#### collation

# les fichiers doivent avoir une première structure de base, avec un @xml:id et un @corresp
# le @corresp pour tous les fichiers sauf le fichier de base doivent correspondre à l'xml:id du fichier de base
# les fichiers doivent être tokénisés (éléments <w>) et porter un élément @xml:id ; cet élément doit idéalement commencer par le sigle du témoin
# car c'est cette valeur qui est récupérée ensuite dans la sortie pour @wit des <rdg> et <lem> ; sinon, ce sera A, B, C, etc.

# définition du dossier où on va récupérer les témoins pour les collationner
# possibilité modifier les valeurs de dossier et de A1
# modifier temBase en fonction du sigle du témoin (doit correspondre également au nom du fichier xml (ex. : "Ao.xml"))
temBase = 'Ao'
dossier = 'fichiers_prod_auto_align_div/Def'
# définition du témoin de base
A1 = etree.parse('fichiers_prod_auto_align_div/Def/'+temBase+'.xml')


### si les documents à collationner sont en TEI :
"""
## donner le nom du dossier dans lequel les fichiers à aligner se trouve
nomDuDossierFichiersTEI = 'docTEIColl'

## application de la fonction qui permet ensuite de retourner du XML manipulable
passerEnXMLBrut(nomDuDossierFichiersTEI)

## les nouveaux fichiers XML bruts se trouvent dans un dossier xml au sein du dossier de base
## c'est ce dossier qui va servir de base à l'itération de la collation
dossier = nomDuDossierFichiersTEI+'/xml'
#dossier = 'docTEIColl/xml'

## donner le nom du fichier de base à partir duquel on va aligner
nomDuFichierDeBase = 'Ao.xml'

## on parse le fichier
A1 = etree.parse(dossier+'/'+nomDuFichierDeBase)
#A1 = etree.parse('docTEIColl/xml/Ao.xml')
"""

## collationParNiveau va permettre de collationner en fonction de la structure initiale du document
# 3 nvx sont supportés
# le 1er doit avoir une structuration de type @xml:id/corresp, avec les élements @corresp qui correspondent au témoin de base
# les deux autres doivent avoir des attributs @n de même valeur
# les arguments sont : A1 : le fichier de base à partir duquel la collation s'effectue ; dossier : le dossier dans lequel les témoins à aligner se trouvent (A1) peut être dans ce dossier ou non ; une valeur textuelle 'lem' ou 'rdg' pour obtenir en sortie à l'intérieur des éléments <app> soit que des <rdg> soit des <rdg> et un <lem> qui sera produit pour les leçons de A1

collationParNiveau(A1,dossier,'lem')



