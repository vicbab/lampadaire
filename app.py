from flask import Flask, render_template, redirect, send_file 
import tools
import config
import pypandoc
import re
import makecaches
import json
import os
from slugify import slugify



app = Flask(__name__, template_folder='./templates/')

if config.dynamic:
    print('dynamic version')
else:
    print('version with caches')
    makecaches.makecaches()

@app.route('/') # route où seront servies ces données
def homepage(): # la fonction qui sert les données pour la route /
    if config.dynamic:
        articles = tools.retrievetags("article")
        appels = tools.retrievetags("appel")
        dossiers = tools.setdossiers()
    else:
        # TODO: fix ceci pour match avec les nouvelles fonctions
        data = json.load(open('caches/articles.json','r'))
    return render_template('index.html', title=config.title, current_page='home', articles=articles, appels=appels, dossiers=dossiers)

@app.route('/contribuer.html') # route où seront servies ces données
def contribuer(): # la fonction qui sert les données pour la route /
    page = "static/pages/contribuer.md"
    contenu = pypandoc.convert_file(page, 'html', format='md')

    return render_template('contribuer.html', current_page='contribuer', title=config.title, contenu=contenu)

@app.route('/a-propos.html') # route où seront servies ces données
def aboutpage(): # la fonction qui sert les données pour la route /
    page = "static/pages/a-propos.md"
    contenu = pypandoc.convert_file(page, 'html', format='md')
    return render_template('a-propos.html', current_page='a-propos', title="À propos - Lampadaire", contenu = contenu)

@app.route('/appels.html') # route où seront servies ces données
def appels(): # la fonction qui sert les données pour la route /
    if config.dynamic:
        data = tools.retrievetags("appel")
        data = sorted(data, key=lambda item: item['myid'], reverse=True)
    else:
        data = json.load(open('caches/appels.json','r'))
    return render_template('appels.html', current_page='appels', title="Appels de textes - Lampadaire", data=data)

@app.route('/contact.html') # route où seront servies ces données
def contact(): # la fonction qui sert les données pour la route /
    page = "static/pages/contact.md"
    contenu = pypandoc.convert_file(page, 'html', format='md')

    return render_template('contact.html', current_page='a-propos', title="Contact - Lampadaire", contenu=contenu)

@app.route('/articles/<myid>.html')
def article(myid):
    alldata=tools.idfrommyid(myid)    # fonction pour récuperer les données d'un article à partir de son id yaml
    data=alldata[0]
    myid=alldata[1]
    yaml=alldata[2]
    try:
        keywords= yaml['keywords']
        
        kw_sl=[]
        for kw in keywords:
            keywords_slugs = [(k, slugify(k)) for k in kw['list_f']]
            kw.update({'list_f':keywords_slugs})
            kw_sl.append(kw)
    except:
        kw_sl=[]
    try:
        authors= yaml['authors']
        
        au_sl=[]
        for au in authors:
            authorslug = slugify(au['surname'])+'-'+slugify(au['forname'])
            au.update({'authorslug':authorslug})
            au_sl.append(au)
            
        
        # TODO: Ici, ajouter le display pour les noms d'auteurs multiples avec un "et"
    except:
        au_sl=[]
    yaml.update({'authors':au_sl})
    title = pypandoc.convert_text(yaml['title_f'], 'html', format='md') 
    try:
        myarticle = pypandoc.convert_text(data['data']['article']['workingVersion']['md'], 'html', format='md', extra_args=['--citeproc', '--bibliography=static/lampadaire.bib', '--csl=https://www.zotero.org/styles/chicago-author-date-fr'])
    except:
        myarticle = data['data']['article']['workingVersion']['md']
    abstract_fr=''
    abstract_en=''
    try:
        for abstract in yaml['abstract']:
            if abstract['lang'] == 'fr':
                abstract_fr = abstract['text_f']
    except:    
        abstract_fr=''
    try:
        for abstract in yaml['abstract']:
            if abstract['lang'] == 'en':
                abstract_en = abstract['text_f']
    except:    
        abstract_en=''
            
    try:
        authors = yaml['authors']
    except:
        authors = [{'forname':'','name':'','orcid':''}]
    
    try:
        for d in yaml['dossier']:
            mydossier = d['title_f']
    except:
        mydossier = ''

    return render_template('article.html', current_page='article', myarticle=myarticle, data=data, yaml=yaml,title=title, abstract_fr=abstract_fr, abstract_en=abstract_en, authors=authors, myid=myid, mydossier=mydossier)

@app.route('/downloads/<myid>')
def articlepdf(myid):

    alldata=tools.idfrommyid(myid)    
    data=alldata[0]
    myid=alldata[1]
    id = alldata[3]
    version=alldata[4]
    print(myid,id,version)
    tools.getpdf(id,myid,version)
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = os.path.join('downloads', f'{myid}.pdf')
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return "File not found", 404

# @app.route('/xml/<myid>')
# def articlexml(myid):
    # alldata=tools.idfrommyid(myid)    
    # data=alldata[0]
    # myid=alldata[1]
    # id = alldata[3]
    # version=alldata[4]
    # # print(myid,id,version)
    # tools.getpdf(id,myid,version)
    # #For windows you need to use drive name [ex: F:/Example.pdf]
    # path = "downloads/"+myid+"-"+id+"/"+myid+"-metopes.tei.xml"
    # return send_file(path, as_attachment=True)

@app.route('/motscles/index.html') # route où seront servies ces données
def keywords(): # la fonction qui sert les données pour la route /
    if config.dynamic:
        data = tools.setkeywords()
    else:
        data = json.load(open('caches/keywords.json','r'))

    data = sorted(data, key=lambda k: k['name']) 
    return render_template('motscles.html', current_page='articles', title="Mots-clés - Lampadaire", data=data)

@app.route('/motscles/<name>.html')
def keyword(name):

    if config.dynamic:
        data = tools.setkeywords()
    else:
        data = json.load(open('caches/keywords.json','r'))
    mykeyword={}
    for k in data:
        if k['nameslug'] == name:
            mykeyword = k
    return render_template('motcle.html', current_page='articles', title= name + " - Lampadaire", mykeyword=mykeyword)

@app.route('/auteurices/index.html') # route où seront servies ces données
def authors(): # la fonction qui sert les données pour la route /
    if config.dynamic:
        data = tools.setauthors()
    else:
        data = json.load(open('caches/authors.json','r'))

    return render_template('authors.html', current_page='articles', title="Auteurices - Lampadaire", data=data)

@app.route('/auteurices/<name>.html')
def author(name):

    if config.dynamic:
        data = tools.setauthors()
    else:
        data = json.load(open('caches/authors.json','r'))
    myauthor={}
    for a in data:
        if a['authorslug'] == name:
            myauthor = a
    return render_template('author.html', current_page='articles', title= name + " - Lampadaire", author=myauthor)

@app.route('/dossiers/index.html') # route où seront servies ces données
def dossiers(): # la fonction qui sert les données pour la route /
    if config.dynamic:
        data = tools.setdossiers()
    else:
        data = json.load(open('caches/dossiers.json','r'))


    return render_template('dossiers.html', current_page='articles', title="Numéros - Lampadaire", data=data)

@app.route('/dossiers/<idd>.html')
def dossier(idd):

    if config.dynamic:
        data = tools.setdossiers()
        
    else:
        data = json.load(open('caches/dossiers.json','r'))
    mydossier={}
    horsdossier={}
    for d in data:
        if d['dossier']['id'] == idd:
            mydossier = d 
        elif d['dossier']['id'] == idd[0:2] + "-ht":
            horsdossier = d
    
    title = mydossier['dossier']['title_f']
    return render_template('dossier.html', current_page='articles', title = title + " - Lampadaire", mydossier=mydossier, horsdossier=horsdossier)

@app.route('/articles.html') # route où seront servies ces données
def articles(): # la fonction qui sert les données pour la route /
    if config.dynamic:
        articles = tools.retrievetags("article")
        appels = tools.retrievetags("appel")
        dossiers = tools.setdossiers()
        authors = tools.setauthors()
    else:
        # TODO: fix ceci pour match avec les nouvelles fonctions
        data = json.load(open('caches/articles.json','r'))
    return render_template('articles.html', current_page='articles', title=config.title, articles=articles, appels=appels, dossiers=dossiers, authors=authors)

@app.route('/appels/<myid>.html')
def appel(myid):
    alldata=tools.idfrommyid(myid)    # fonction pour récuperer les données d'un article à partir de son id yaml
    data=alldata[0]
    myid=alldata[1]
    yaml=alldata[2]
   
    title = pypandoc.convert_text(yaml['title_f'], 'html', format='md') 
    try:
        myarticle = pypandoc.convert_text(data['data']['article']['workingVersion']['md'], 'html', format='md', extra_args=['--citeproc', '--bibliography=static/lampadaire.bib', '--csl=https://www.zotero.org/styles/chicago-author-date-fr'])
    except:
        myarticle = data['data']['article']['workingVersion']['md']

    return render_template('appel.html', current_page='appels', myarticle=myarticle, data=data, yaml=yaml, title=title, myid=myid)




if __name__ == '__main__':
  app.run(debug=True, port=3000)
