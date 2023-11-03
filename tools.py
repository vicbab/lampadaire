import requests
import json
import config
import yaml
import re
import pypandoc
import zipfile, io
from slugify import slugify
import traceback
import os

endpoint = "https://stylo.huma-num.fr/graphql"
headers = {"Authorization": f"Bearer {config.accessToken}"}


# une fonction pour transformer le yaml en json car je suis plus à l'aise
def yamltojs(myyaml):
    sourcesyaml = yaml.load_all(myyaml, Loader=yaml.Loader)
    sourcesjs=[]
    for source in sourcesyaml:
        sourcesjs.append(source)
    return sourcesjs

# fonction pour récuperer les données d'un article à partir de son id yaml
def idfrommyid(myid):

    id=myid #cela permet de faire fonctionner l'application avec les id stylo. dans ce cas la fonction returnera id=myid
    if config.dynamic:
        la = retrievetags("both")
    else:
        la = json.load(open('caches/articles.json','r'))
    for i in la:
        try:
            myart = i['myid']

            if myart == myid:
                id = i['id']
        except:
            continue
    
    if config.dynamic:
        data = retrievearticle(id)
    else:
        data = ""
        for i in la:
            if i['myid'] == myid:
                data = {'data':{'article':i}}
        if data == "": # si l'article n'a pas d'id yaml
          for i in la:
            if i['id'] == myid:
                data = {'data':{'article':i}}
    yaml = yamltojs(data['data']['article']['workingVersion']['yaml'])[0]
    
    try:
        latestversion= data['data']['article']['versions'][0]['_id']
    except:
        latestversion=""
    try:
        myid_def = re.split("_", yamltojs(data['data']['article']['workingVersion']['yaml'])[0]['id'])[0]
    except:
        myid_def=''
    return [data, myid_def, yaml, id,latestversion]    

def getartinfofromyaml(article,key):
    try:
        value = yamltojs(article['workingVersion']['yaml'])[0][key]
    except:
        value = ''
    return value


# fonction pour récuperer le pdf via l'export stylo. Si on crée un export pour femur, on pourra avoir un template particulier et récuperer aussi l'xml
def getpdf(article, myid, version):
    print("getting "+article)
    print(myid)
    url ="https://export.stylo.huma-num.fr/generique/export/stylo.huma-num.fr/"+article+"/"+myid+"/"
    print(url)
    params = {
                "with_toc": 0,
                "with_ascii": 0,
                "version": version,
                "bibliography_style": "chicagomodified",
                "formats": "pdf",
                }
    r = requests.get(url,params)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    print(z.filelist)
    z.extractall("downloads")
    for file in z.filelist:
        new_file_name = f'{myid}.pdf'
        new_file_path = f'downloads/{new_file_name}'
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
        os.rename(f'downloads/{file.filename}', new_file_path)
        
def getxml(article, myid, version):
    print("getting "+article)
    url ="https://export.stylo.huma-num.fr/generique/export/stylo.huma-num.fr/"+article+"/"+myid+"/"
    params = {
                "with_toc": 0,
                "with_ascii": 0,
                "version": version,
                "bibliography_style": "chicagomodified",
                "formats": "xml-tei-metopes-1",
                }
    r = requests.get(url,params)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    # print("zipfile:" + z.filelist)
    z.extractall("downloads")

def retrievetags(type):
    query = """
    
    {
      
        
          articles{_id title workingVersion{yaml} tags{name} }
          
          
        
      }
    
    
    """
    
    r = requests.post(endpoint, json={"query": query}, headers=headers)
    if r.status_code == 200:
        articlesdata = r.json()['data']['articles']

        # tagName = ""
        
        skipAuthors = False
        

        tagNames = []

        if type == "article":
            tagNames.append(config.tagName)
        elif type == "appel":
            tagNames.append(config.appelTag)
            skipAuthors = True
        elif type == "both":
            tagNames.append(config.tagName)
            tagNames.append(config.appelTag)
            # skip = True

        articles=[]
        for article in articlesdata:
            try:  
                for tag in article['tags']:
                    if tag['name'] in tagNames:
                        titledoc=article['title']

                        idart= article['_id'] 
                        yaml = yamltojs(article['workingVersion']['yaml'])[0] 
                        
                        myid=re.split('_', getartinfofromyaml(article,'id'))[0]  
                        
                        

                        try:
                            title = pypandoc.convert_text(yaml['title_f'], 'html', format='md')
                        except:
                            title = article['title']

                        

                        # if "Appel" in title:
                        #     skipAuthors = True

                        if skipAuthors:
                            display = title
                        else:
                            authors = yaml['authors']
                            display = getdisplay(authors, title)

                        # authors = yaml['authors']
                        # display = getdisplay(authors, title)

                        dictart = {"titledoc":titledoc, "id":idart, "yaml":yaml, 'myid':myid, 'title':title, 'display':display} 

                        if dictart not in articles:
                            articles.append(dictart)

                    # if tag['name'] == tagName or skip:
                    #     titledoc=article['title']

                    #     idart= article['_id'] 
                    #     yaml = yamltojs(article['workingVersion']['yaml'])[0] 
                        
                    #     myid=re.split('_', getartinfofromyaml(article,'id'))[0]  
                        
                        

                    #     try:
                    #         title = pypandoc.convert_text(yaml['title_f'], 'html', format='md')
                    #     except:
                    #         title = article['title']

                    #     authors = yaml['authors']
                    #     display = title

                    #     dictart = {"titledoc":titledoc, "id":idart, "yaml":yaml, 'myid':myid, 'title':title, 'display':display} 

                    #     if dictart not in articles:
                    #         articles.append(dictart)             
            except:
                traceback.print_exc()
                continue
            

        return articles
    else:
        raise Exception(f"Query failed to run with a {r.status_code}.")

def retrievearticle(article):
    query = '{article(article:"'+article+'"){_id title contributors{user{displayName}} workingVersion{md yaml bib}versions{_id} }}'

    r = requests.post(endpoint, json={"query": query}, headers=headers)
    if r.status_code == 200:
        data = r.json()
        data.update({'myid':getartinfofromyaml(data['data']['article'],'id')})
        return data
    else:
        raise Exception(f"Query failed to run with a {r.status_code}.")

def retrievekeywords():
    key_fr=[]
    data = retrievetags("article")
    for article in data:
        article_id = article['id']
        myid = article['myid']
        try:
           keywords = article['yaml']['keywords']
           for k in keywords:
               if k['lang'] == 'fr':
                   for kf in k['list_f']:
                       try:
                           title=article['title']
                       except:
                           title=''
                       articles_list={'myid':myid, 'id':article_id, 'title':title}
                       nameslug=slugify(kf)
                       dictkey = {'name': kf, 'nameslug':nameslug,'articles': articles_list}

                       key_fr.append(dictkey)
        except:
            continue
                
    return key_fr

def retrievedossiers():
    dossiers=[]
    for article in retrievetags("article"):
        
        article_id = article['id']
        myid = article['myid']
        dossier = article['yaml']['dossier']
        title= article['title']
        authors = article['yaml']['authors']
        display = getdisplay(authors, title)
       
        # print(article['authors'])
        articles_list={'myid':myid,'id':article_id, 'title':title, 'display':display}
        dictdossier = {'dossier': dossier[0], 'articles': articles_list}
        dossiers.append(dictdossier)
                        
     
    return dossiers

def getdisplay(authors, title):
    authors_list = []
    for author in authors:
        try:
            surname = author['surname']
        except:
            surname = ""
        try:
            forname = author['forname']
        except:
            forname = ""
        name = forname + " " + surname

        dictauthor = {'name':name}
        authors_list.append(dictauthor)
        
    names = formatnames(authors_list)

    return names + title

def formatnames(authors):
    names = ""
    i = 1
    for author in authors:
        names = names + author['name']
        
        if i < len(authors):
            names = names + " et "
        i += 1

    names = names + ", "    
    return names

def retrieveauthors():
    authors_list=[]
    for article in retrievetags("article"):
        article_id = article['id']
        myid = article['myid']
        try:
            authors = article['yaml']['authors']
            for author in authors:
                title= article['title']
                articles_list={'myid':myid,'id':article_id, 'title':title}
                authornslug = slugify(author['surname'])
                authorfslug = slugify(author['forname'])
                authorslug= authornslug+'-'+authorfslug
                dictauthor = {'author': author, 'authorslug':authorslug, 'articles': articles_list}
                authors_list.append(dictauthor)
        except:
            continue

     
    return authors_list


   #une fonction pour enlever tous les doublons et mettre les articles de chaque mot-clé dans une liste. Avant, la fonction retrievekeywords() fait une liste de dictionnaires avec tous les mots-clés et les articles liés, mais avec répetitions, par ex: [{'name':'portrait', 'article':1},{'name':'portrait', 'article':2}]. La fonction qui suit transforme en:  [{'name':'portrait', 'article':[1,2]}]
def setkeywords():
    keywords = retrievekeywords()
    sansdoublons= set([k['name'] for k in keywords])
    liste_sd=[]        
    for name in sansdoublons:
        dictk = {'name':name}
        lista=[]
        for kw in keywords:
            if kw['name']== name:
                lista.append(kw['articles'])
                dictk.update({'nameslug':kw['nameslug']})
        dictk.update({'articles':lista })        
        liste_sd.append(dictk)    
    return liste_sd    
def setdossiers():
    dossiers = retrievedossiers()
    dossierssorted = sorted(dossiers, key=lambda k: k['dossier']['id']) 
    seen = []
    new_l = []
    for d in dossierssorted:
        if d['dossier']['id'] not in seen:
            if d['dossier']['id'] == '':
                continue
            else:
                seen.append(d['dossier']['id'])
                new_l.append(d['dossier'])

    liste_dict_dossiers= []
    for d in new_l:
        liste_sd = []        
        dictd={'dossier':d}
        for i in dossierssorted:
            if i['dossier']['id'] == d['id']:
                liste_sd.append(i['articles'])
        liste_sd = sorted(liste_sd, key=lambda k: k['myid']) 
        dictd.update({'articles':liste_sd})        
        liste_dict_dossiers.append(dictd)    
    return liste_dict_dossiers    


def setauthors():
    authors = retrieveauthors()
    authorssorted = sorted(authors, key=lambda k: k['author']['surname']) 
    seen = []
    new_l = []
    for a in authorssorted:
        if (a['author']['forname'], a['author']['surname']) not in seen: ## attention: ça marche pas s'il y a des homonimes (même nom, même prénom)
            seen.append((a['author']['forname'], a['author']['surname']))
            new_l.append(a['author'])

    liste_dict_authors= []
    for a in new_l:
        liste_sd = []        
        dicta={'author':a}
        for i in authorssorted:
            if i['author']['forname'] == a['forname'] and i['author']['surname'] == a['surname']:
                liste_sd.append(i['articles'])
                dicta.update({'authorslug': i['authorslug']})
                try: 
                    bio = pypandoc.convert_text(i['author']['biography'], 'html', format='md') 
                    
                        
                    a.update({'biography':bio})    



                except KeyError:
                    continue
        liste_sd = sorted(liste_sd, key=lambda k: k['myid']) 
        dicta.update({'articles':liste_sd})        
        liste_dict_authors.append(dicta)    
    return liste_dict_authors    
