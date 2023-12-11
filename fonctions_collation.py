#!usr/bin/env python
# -*- coding: utf-8 -*-

#import des librairies nécessaires
#attention : nommer différemment ElementTree et etree, et appeler le deuxième pour la fonction notre_export_table sinon pas possible de produire xml:id --> conflit ?
from lxml import etree
from xml.etree import ElementTree as et
from collatex import *
from collatex.edit_graph_aligner import *
from collatex.core_classes import *
from collatex.near_matching import *
import json
import graphviz
import re, os
from prettytable import PrettyTable
from textwrap import fill
from io import StringIO

#défintion de la transformation vers du json
def XMLtoJson(id,xmlInput):
    # converts an XML tokenised and annotated input to JSON for collation
    witness = {}
    witness['id'] = id
    monXSL = etree.XML('''
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="1.0">

    <xsl:output method="text"/>

    <xsl:template match="/">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="w">
        <xsl:text>{"text": "</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>", "i": "</xsl:text>
        <xsl:value-of select="@xml:id"/>
        <!-- t est sur quoi la coll va se réaliser : si lemme, on met valeur de lemme -->
        <xsl:text>", "t": "</xsl:text>
        <xsl:choose>
            <xsl:when test="@lemma">
                <xsl:value-of select="@lemma"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates/>
            </xsl:otherwise>
        </xsl:choose>
        <!-- pour produire un document conforme ensuite à la structure de base, on rajouter un autre élément l -->
        <xsl:text>", "l" :"</xsl:text>
        <xsl:value-of select="@lemma"/>
        <xsl:text>", "pos": "</xsl:text>
        <xsl:value-of select="@pos"/>
        <xsl:text>", "msd":"</xsl:text>
        <xsl:value-of select="@msd"/>
        <xsl:text>"}</xsl:text>
        <xsl:if test="following::w">
            <xsl:text>, </xsl:text>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
    ''')
    monXSL = etree.XSLT(monXSL)
    witness['tokens'] = json.loads( '[' +str(monXSL(xmlInput)) +']')
    return witness

#définition de l'export qui nous convient
def notre_export_xml(table,lemrdg):
    readings = []
    for column in table.columns:
        app = et.Element('app')
        for key, value in sorted(column.tokens_per_witness.items()):
            ## ajout pour lem
            if lemrdg == 'lem' and key == 'A':
                child = et.Element('lem')
            else:
                child = et.Element('rdg')
            
                ### à modifier ici pour retourner un doc TEI propre avec app/lem|rdg/w
            #modif ici pour garder tous les éléments de nos mots
            for item in value:
                idSigle = item.token_data["i"].split('_')[0]
                if idSigle != None:
                    child.attrib['wit'] = "#" + idSigle
                else:
                    child.attrib['wit'] = "#" + key
                word = et.SubElement(child, "w")
                word.attrib['xml:id'] = item.token_data["i"]
                if item.token_data['l'] != '':
                    word.attrib['lemma']= item.token_data["t"]
                else:
                    pass
                if item.token_data["pos"] != '':
                    word.attrib['pos'] = item.token_data["pos"]
                else:
                    pass
                if item.token_data["msd"] != '':
                    word.attrib['msd'] = item.token_data["msd"]
                else:
                    pass
                #fin modif
            word.text = "".join(str(item.token_data["text"]) for item in value)
            app.append(child)
        # Without the encoding specification, outputs bytes instead of a string
        result = et.tostring(app, encoding="unicode")
        readings.append(result)
    return "".join(readings)
    
#redéfintion de l'export des tables, sur les tokens directement
def notretable(table):
    # print the table vertically
    x = PrettyTable()
    x.hrules = 1
    for row in table.rows:
        # x.add_column(row.header, [fill(cell.token_data["t"], 20) if cell else "-" for cell in row.cells])
        t_list = [(token.token_data["text"] for token in cell) if cell else ["-"] for cell in row.cells]
        x.add_column(row.header, [fill("".join(item), 20) for item in t_list])
    return x

def laCollation(inputJson,iDiv,i,lemrdg):        
    layout="vertical"
    #scheduler=Scheduler()

    #création de l'objet collation
    collation = inputJson
    i = i
    json_collation = Collation()
    for witness in collation["witnesses"]:
        json_collation.add_witness(witness)
    collation = json_collation
    print(collation)
    
    algorithm = EditGraphAligner(collation)
    # construction du graphe
    graph = VariantGraph()
        #algorithm.collate(graph, collation)
    algorithm.collate(graph)
    ranking = VariantGraphRanking.of(graph)
    highestRank = ranking.byVertex[graph.end]
    witnessCount = len(collation.witnesses)
    # construction du fonctionement
    rank = highestRank - 1
    ranking = VariantGraphRanking.of(graph)
    table = AlignmentTable(collation, graph, layout, ranking)
    
    #on fait appel à notre propre fonction table pour créer des tables comme on le souhaite
    t = notretable(table)
    print(t)
    tables = str(t)
    if not os.path.isdir("tables"):
        os.makedirs("tables")
    if i != 000:
        with open("./tables/table_"+iDiv[3:6]+"_"+i, "w") as w:
            w.write(tables)
    else:
        with open("./tables/table_"+iDiv[3:6]+'"', "w") as w:
            w.write(tables)
    #appel de la fonction notre_export

    ## besoin de faire deux exports : un avec lem/rdg et autre juste avec rdg
    if lemrdg == 'lem':
        result = notre_export_xml(table,'lem')
    else:
        result = notre_export_xml(table,'rdg')

    return result

## tout passer depuis TEI
def passerEnXMLBrut(dossier):
    try:
        os.mkdir(dossier+"/xml")
    except OSError:
        pass
    for filename in os.listdir(dossier):
        if os.path.isfile(os.path.join(dossier, filename)):
            f = os.path.join(dossier, filename)
            print('fichier : '+f)
            nom = str(filename).split('.')[0]
            doc = etree.parse(f)
            root_element = doc.getroot()
            fromTEI(root_element, nom, dossier)
        else:
            pass    

## transfo depuis TEI
def fromTEI(docenTEI,sigle,dossier):
    sigle = sigle
    print(sigle)
    tei_ns = 'http://www.tei-c.org/ns/1.0'
    ns_decl = {'tei': tei_ns}

    new_root = etree.Element("text")
    current_paragraph = None
    # Parcourir les éléments du document XML d'origine
    for element in docenTEI.xpath(f"descendant::node()[self::tei:w or self::tei:p or self::tei:div or self::tei:lg or self::tei:l or self::tei:ab]", namespaces=ns_decl):
        if element.xpath(f"descendant::node()[self::tei:p or self::tei:div or self::tei:lg or self::tei:l or self::tei:ab] and @xml:id", namespaces=ns_decl):
            nomElem = etree.QName(element).localname
            current_paragraph = None
            new_div = etree.SubElement(new_root, nomElem)
            new_div.attrib.update(element.attrib)
        elif element.tag == "{http://www.tei-c.org/ns/1.0}w":
            # Si c'est un mot, l'ajouter au paragraphe en cours ou créer un nouveau paragraphe
            if current_paragraph is None:
                current_paragraph = etree.SubElement(new_div, "p")
            new_word = etree.SubElement(current_paragraph, "w")
            new_word.attrib.update(element.attrib)
            new_word.text = element.text
        elif element.xpath(f"ancestor::node()[self::tei:div or self::tei:lg or self::tei:ab][@n]", namespaces=ns_decl):
            # Si c'est une unité plus petite, mettre à jour l'unité en cours
            nomElemNivBas = etree.QName(element).localname
            current_paragraph = etree.SubElement(new_div, nomElemNivBas)
                    
    docXML = etree.tostring(new_root, encoding="UTF-8")
    docXML_str = docXML.decode("UTF-8")

    print(docXML)
    print(sigle)
    with open(dossier+"/xml/"+sigle+".xml", "w") as text_file:
        text_file.write(docXML_str)
    return docXML
    


## fonction de la collation en fonction des différents nvx
## on donne le fichier de base (A1), le dossier sur lequel on va itérer, et si on veut en sortie un <lem> ou que des <rdg> dans les <app>
def collationParNiveau(temBase, dossier, lemRdg):
#création d'une liste vide
    v = []
    vDiv = []
    propreId = 1
    A1 = temBase
    # parser les différents éléments 

    for div in A1.xpath(f"//text//child::node()[(self::l or self::p or self::div or self::lg or self::ab) and @xml:id]"):
        nomElem = str(div.xpath("name()"))
        print(nomElem)
        iDiv = div.get('{http://www.w3.org/XML/1998/namespace}id')
        print(iDiv)
        vSubp = []

        if A1.xpath("//text//child::node()[@xml:id='"+iDiv+"']/child::node()[(self::l or self::p or self::div or self::lg or self::ab) and @n]"):
        ## niv 3 (ex: div@xml:id/div@n/p@n)
            for par in A1.xpath("//text//child::node()[@xml:id='"+iDiv+"']/child::node()[(self::l or self::p or self::div or self::lg or self::ab) and @n]"):
                iPar = par.get('n')
                print(iPar)
                nomElemNiv2 = str(par.xpath("name()"))
                if A1.xpath("//text//child::node()[@xml:id='"+iDiv+"']/child::node()[@n='"+iPar+"']/child::node()[(self::l or self::p or self::ab) and @n]"):
                
                    print(iPar)
                    for subpar in A1.xpath("//text//child::node()[@xml:id='"+iDiv+"']/child::node()[@n='"+iPar+"']/child::node()[(self::l or self::p or self::ab) and @n]"):
                        #initialisation du json input
                        json_input = {}
                        json_input['witnesses'] = []
                        # récupération du nom de l'élément
                        nomElemNiv3 = str(subpar.xpath("name()"))
                        #on récupère le numéro de paragraphe
                        i = subpar.get('n')
                        # on vérifie que tout se passe bien
                        print(i)
                        #A = le paragraphe en question
                        A = subpar
                        print(A)
                        json_input['witnesses'].append(XMLtoJson('A',A))
                        x=1
                        # ouverture d'une liste pour les id des corr
                        listeId = []
                        for filename in os.listdir(dossier):
                            f = os.path.join(dossier, filename)
                            B1 = etree.parse(f)
                            aT= str(chr(x+65))
                            for divEz in B1.xpath("//text//child::node()[@corresp='"+iDiv+"']"):
                                iDivEz = divEz.get('{http://www.w3.org/XML/1998/namespace}id')
                                print(iDivEz)
                                listeId.append(iDivEz)
                                if B1.xpath("//text//child::node()[@corresp='"+iDiv+"']/child::node()[(self::l or self::p or self::div or self::lg or self::ab) and @n='"+iPar+"']/child::node()[(self::l or self::p or self::ab) and @n='"+i+"']"):
                                    for sp in B1.xpath(f"//text//child::node()[@xml:id='"+iDivEz+"']/child::node()[(self::l or self::p or self::div or self::lg or self::ab) and @n='"+iPar+"']/child::node()[(self::l or self::p or self::ab) and @n='"+i+"']"):
                                        #B = le paragraphe qui porte le même numéro que en A
                                        B = sp
                                        json_input['witnesses'].append(XMLtoJson(str(aT),B))
                                else:
                                    pass
                            x+=1
                            print(x)
                        listeId = '-'.join(listeId)    
                        print(json_input)
                        idParSubPar = ''.join([iPar,i])
                        objetColl = laCollation(json_input,iDiv,idParSubPar,lemRdg)
                        result = objetColl
                        print(result)
                        doc = '<'+nomElemNiv3+' n="' + i +'">' + result + '</'+nomElemNiv3+'>'
                        #on remplit la liste vSubp au fur et à mesure
                        vSubp.append(doc)

                    #ici niv intermédiaire    
                    valPar =  '<'+nomElemNiv2+' n="'+iPar+'">'+''.join(vSubp) +  '</'+nomElemNiv2+'>'  

                    v.append(valPar)
                    vSubp = []

                ### 2 nvx
                else : 
                #initialisation du json input
                    json_input = {}
                    json_input['witnesses'] = []
                    #récupération du nom de l'élément
                    nomElemNiv2 = str(par.xpath("name()"))
                    #on récupère le numéro de paragraphe
                    i = par.get('n')
                    # on vérifie que tout se passe bien
                    print(i)
                    #A = le paragraphe en question
                    A = par
                    print(A)
                    json_input['witnesses'].append(XMLtoJson('A',A))
                    x=1
                    # ouverture d'une liste pour les id des corr
                    listeId = []
                    for filename in os.listdir(dossier):
                        f = os.path.join(dossier, filename)
                        B1 = etree.parse(f)
                        aT= str(chr(x+65))
                        for divEz in B1.xpath("//text//child::node()[@corresp='"+iDiv+"']"):
                            iDivEz = divEz.get('{http://www.w3.org/XML/1998/namespace}id')
                            print(iDivEz)
                            listeId.append(iDivEz)
                            if B1.xpath("//text//child::node()[@corresp='"+iDiv+"']/child::node()[self::l or self::p or self::div or self::lg or self::ab]"):
                                for p in B1.xpath(f"//text//child::node()[@xml:id='"+iDivEz+"']/child::node()[self::l or self::p or self::div or self::lg or self::ab][@n='"+i+"']"):
                                    #B = le paragraphe qui porte le même numéro que en A
                                    B = p
                                    json_input['witnesses'].append(XMLtoJson(str(aT),B))
                            else:
                                pass
                        x+=1
                        print(x)
                    listeId = '-'.join(listeId)    
                    objetColl = laCollation(json_input,iDiv,i,lemRdg)
                    result = objetColl
                    print(result)
                    doc = '<'+nomElemNiv2+' n="' + i +'">' + result + '</'+nomElemNiv2+'>'
                    #on remplit la liste v au fur et à mesure
                    v.append(doc)

                    #ajout pour réunir les div    
            valDiv =  '<'+nomElem+' xml:id="divColl' + str(propreId) +'" corresp="' + iDiv +'-'+ listeId +'">'+''.join(v) +  '</'+nomElem+'>'
            v = []

        # 1 nv
        else:
            json_input = {}
            json_input['witnesses'] = []
            # ouverture d'une liste pour les id des corr
            listeId = []
            A = div
            json_input['witnesses'].append(XMLtoJson('A',A))
            x=1
            for filename in os.listdir(dossier):
                f = os.path.join(dossier, filename)
                B1 = etree.parse(f)
                print(B1)
                aT= str(chr(x+65))
                if B1.xpath("//text//child::node()[@corresp='"+iDiv+"']"):
                    for divEz in B1.xpath("//text//child::node()[@corresp='"+iDiv+"']"):
                        iDivEz = divEz.get('{http://www.w3.org/XML/1998/namespace}id')
                        listeId.append(iDivEz)
                        B = divEz
                        json_input['witnesses'].append(XMLtoJson(str(aT),B))
                else:
                    pass
                x+=1
            listeId = '-'.join(listeId)
            print(json_input)
            objetColl = laCollation(json_input,iDiv,000,lemRdg) 
            result = objetColl
            #ajout pour réunir les div    
            valDiv = '<'+nomElem+' xml:id="divColl' + str(propreId) +'" corresp="' + iDiv +'_'+ listeId +'">'+ result +  '</'+nomElem+'>'
        if not os.path.isdir("collParDiv"):
            os.makedirs("collParDiv")
        with open("collParDiv/collationDiv"+iDiv[3:6]+".xml", "w") as text_file:
            text_file.write(valDiv) 
        vDiv.append(valDiv)
        propreId+=1
        valDiv = []

        # on crée un objet dans lequel on place notre liste, à l'intérieur d'une balise racine <text>
        # ne renvoie pas un document TEI propre
    val = "<text>" + ''.join(vDiv) + "</text>"
    with open("resultat_collation.xml", "w") as text_file:
        text_file.write(val) 


