# alignementEtCollation
Le dépôt contient des scripts pour permettre l'alignement macro et micro de textes. Les scripts font appel aux librairies collatex et text_matcher.

Il est possible d'exécuter le script alignementEtCollation.py ou simplement alignement.py (alignement macro) ou collation.py (alignement mot à mot).

Ils doivent être composés d'un premier niveau de structuration. Ces éléments doivent avoir des attributs @xml:id et @corresp. L'un des fichiers doit être considéré comme le fichier de base, avec lequel chacun des autres fichiers sera comparé. L'attribut @corresp des témoins doit renvoyer à l'@xml:id des divisions du témoin considéré comme témoin de base.

Les fichiers doivent être tokénisés (éléments w disposant d'un @xml:id). Ils peuvent ou non être dotés d'une annotation linguistique (attributs @lemma, @pos, @msd supportés).

## alignement

Les fichiers à aligner doivent être en TEI et avoir un premier niveau de structuration.
L'alignement permet la division en plus petites unités d'unités importantes. Il permet la création de paragraphes correspondants (identifiés d'un document à l'autre avec une même valeur de @n à l'intérieur de chacune des divisions de niveau 1). 
Attention, l'alignement écrase tout autre niveau de structuration ; il est basé sur des suites de tokens similaires et ne respecte donc pas les unités de sens.

## collation
Les fichiers à collationner doivent être en XML ou en TEI. La collation supporte jusqu'à trois niveaux de structuration initiale, qui doit être construite avec @xml:id/@corresp|@n|@n.
Exemple : on pourra donc avoir un premier niveau de structuration de div, puis un second niveau lg [@n] puis un troisième niveau l [@n].


Par défaut, ce sont les documents qui se trouvent dans le dossier textes/ qui vont être alignés. La collation s'effectue sur les fichiers qui se trouvent dans fichiers_prod_auto_align_div/Def/.
Il s'agit d'extraits du _Lancelot en prose_. Il y a trois documents dans chacun des dossiers, mais le témoin C est seulement un élément dupliqué de Ez.


Le travail à vocation à être amélioré (meilleure gestion des types de documents en entrée et en sortie ; implémentation en ligne de commande ; amélioration de la qualité de l'alignement).


