from flask_frozen import Freezer
from app import app
import tools
import config
import json
import os

freezer = Freezer(app)

@freezer.register_generator
def article():
    if config.dynamic:
        data = tools.retrievetags("both")
    else:
        data = json.load(open('caches/articles.json','r'))
    for article in data :
        if article['myid'] == '':
            yield {'myid': article['id']}
        else:    
            yield {'myid': article['myid']}

@freezer.register_generator
def dossier():
    if config.dynamic:
        data = tools.setdossiers()
    else:
        data = json.load(open('caches/dossiers.json','r'))
    for d in data :
        yield {'idd': d['dossier']['id']}

@freezer.register_generator
def keyword():
    if config.dynamic:
        data = tools.setkeywords()
    else:
        data = json.load(open('caches/keywords.json','r'))
    for d in data :
        yield {'name': d['nameslug']}

@freezer.register_generator
def articlepdf():
    if config.dynamic:
        data = tools.retrievetags("both")
    else:
        data = json.load(open('caches/articles.json','r'))
    for article in data :
        if article['myid'] == '':
            print("1" + article['id'])
            yield {'myid': article['id'] + '.pdf'}
        else:    
            print("2" + article['myid'])
            print({'myid': article['myid']})
            
            yield {'myid': article['myid']}
            old_file_name = "build/downloads/" + article['myid']
            new_file_name = old_file_name + '.pdf'

            os.rename(old_file_name, new_file_name)

if __name__ == '__main__':
    freezer.freeze()
