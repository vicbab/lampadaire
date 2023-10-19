from flask import Flask, render_template, redirect, send_file 
import tools
import config
import pypandoc
import re
import makecaches
import json
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
        data = tools.retrievetags("article")
    else:
        data = json.load(open('caches/articles.json','r'))
    return render_template('index.html', title=config.title, data=data)

@app.route('/a-propos') # route où seront servies ces données
def aboutpage(): # la fonction qui sert les données pour la route /
    return render_template('a-propos.html', title="à propos - revue lampadaire")

@app.route('/appels') # route où seront servies ces données
def appels(): # la fonction qui sert les données pour la route /
    if config.dynamic:
        data = tools.retrievetags("appel")
    else:
        data = json.load(open('caches/appels.json','r'))
    return render_template('appels.html', title="appels de textes - revue lampadaire", data=data)

@app.route('/contact') # route où seront servies ces données
def contact(): # la fonction qui sert les données pour la route /
    return render_template('contact.html', title="contact - revue lampadaire")

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
    except:
        au_sl=[]
    yaml.update({'authors':au_sl})
    title = pypandoc.convert_text(yaml['title_f'], 'html', format='md') 
    try:
        myarticle = pypandoc.convert_text(data['data']['article']['workingVersion']['md'], 'html', format='md')
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

    return render_template('article.html', myarticle=myarticle, data=data, yaml=yaml,title=title, abstract_fr=abstract_fr, abstract_en=abstract_en, authors=authors, myid=myid, mydossier=mydossier)

@app.route('/downloads/<myid>')
def articlepdf(myid):

    alldata=tools.idfrommyid(myid)    
    data=alldata[0]
    myid=alldata[1]
    id = alldata[3]
    version=alldata[4]
    # print(myid,id,version)
    tools.getpdf(id,myid,version)
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = "downloads/"+myid+"-"+id+"/"+myid+".pdf"
    return send_file(path, as_attachment=True)

@app.route('/xml/<myid>')
def articlexml(myid):

    alldata=tools.idfrommyid(myid)    
    data=alldata[0]
    myid=alldata[1]
    id = alldata[3]
    version=alldata[4]
    # print(myid,id,version)
    tools.getpdf(id,myid,version)
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = "downloads/"+myid+"-"+id+"/"+myid+"-metopes.tei.xml"
    return send_file(path, as_attachment=True)

@app.route('/motscles/index.html') # route où seront servies ces données
def keywords(): # la fonction qui sert les données pour la route /
    if config.dynamic:
        data = tools.setkeywords()
    else:
        data = json.load(open('caches/keywords.json','r'))

    data = sorted(data, key=lambda k: k['name']) 
    return render_template('motscles.html', data=data)

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
    return render_template('motcle.html', mykeyword=mykeyword)

@app.route('/authors/index.html') # route où seront servies ces données
def authors(): # la fonction qui sert les données pour la route /
    if config.dynamic:
        data = tools.setauthors()
    else:
        data = json.load(open('caches/authors.json','r'))

    return render_template('authors.html', data=data)

@app.route('/authors/<name>.html')
def author(name):

    if config.dynamic:
        data = tools.setauthors()
    else:
        data = json.load(open('caches/authors.json','r'))
    author={}
    for a in data:
        if a['authorslug'] == name:
            myauthor = a
    return render_template('author.html', author=myauthor)

@app.route('/dossiers/index.html') # route où seront servies ces données
def dossiers(): # la fonction qui sert les données pour la route /
    if config.dynamic:
        data = tools.setdossiers()
    else:
        data = json.load(open('caches/dossiers.json','r'))
    return render_template('dossiers.html', data=data)

@app.route('/dossiers/<idd>.html')
def dossier(idd):

    if config.dynamic:
        data = tools.setdossiers()
    else:
        data = json.load(open('caches/dossiers.json','r'))
    mydossier={}
    for d in data:
        if d['dossier']['id'] == idd:
            mydossier = d 
    return render_template('dossier.html', mydossier=mydossier)

if __name__ == '__main__':
  app.run(debug=True)
