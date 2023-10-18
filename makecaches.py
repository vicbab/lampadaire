import requests
import json
import config
import yaml
import pypandoc
import re
import config
from tools import yamltojs, getartinfofromyaml, setkeywords, setdossiers, setauthors

headers = {"Authorization": f"Bearer {config.accessToken}"}
endpoint = "https://stylo.huma-num.fr/graphql"

def retrievejsoncache():
    query = """
    
    {
      
          articles{_id title contributors{user{displayName}} workingVersion{md yaml bib}versions{_id} tags{name}}
          
          
        
      
    }
    
    """
    
    r = requests.post(endpoint, json={"query": query}, headers=headers)
    if r.status_code == 200:
        articlesdata = r.json()['data']['articles']
        tagName = config.tagName
        articles=[]
        for article in articlesdata:
            try:  
                for tag in article['tags']:
                    if tag['name'] == tagName:
                        titledoc=article['title']
                        idart= article['_id'] 
                        yaml = yamltojs(article['workingVersion']['yaml'])[0] 
                        myid=re.split('_', getartinfofromyaml(article,'id'))[0]  
                        try:
                            title = pypandoc.convert_text(yaml['title_f'], 'html', format='md')
                        except:
                            title = article['title']
                        versions = article['versions']
                        contributors = article['contributors']
                        workingVersion = article['workingVersion']
                        dictart = {"titledoc":titledoc, "id":idart, "yaml":yaml, 'myid':myid, 'title':title, 'versions': versions, 'contributors':contributors, 'workingVersion':workingVersion } 
                        if dictart not in articles:
                            articles.append(dictart)
            except:
                print('no tags')
     
        return articles
    else:
        raise Exception(f"Query failed to run with a {r.status_code}.")


def makecaches():
    with open('caches/articles.json', 'w') as file:
        json.dump(retrievejsoncache(), file)
        
    with open('caches/keywords.json', 'w') as file:
        json.dump(setkeywords(), file)
    with open('caches/dossiers.json', 'w') as file:
        json.dump(setdossiers(), file)
    with open('caches/authors.json', 'w') as file:
        json.dump(setauthors(), file)
