from flask_frozen import Freezer
from app import app
import tools
import config
import json
import os

freezer = Freezer(app)

# @freezer.register_generator
# def article():
#     print("generating articles")
#     if config.dynamic:
#         data = tools.retrievetags("article")
#     else:
#         data = json.load(open('caches/articles.json','r'))
#     for article in data :
#         if article['myid'] == '':
#             yield {'myid': article['id']}
#         else:    
#             yield {'myid': article['myid']}

# @freezer.register_generator
# def appel():
#     print("generating appels")
#     if config.dynamic:
#         data = tools.retrievetags("appel")
#     else:
#         data = json.load(open('caches/appels.json','r'))
#     for appel in data :
#         if appel['myid'] == '':
#             yield {'myid': appel['id']}
#         else:    
#             yield {'myid': appel['myid']}

# @freezer.register_generator
# def dossier():
#     print("generating dossiers")
#     if config.dynamic:
#         print("dynamic: setting dossiers")
#         data = tools.setdossiers()
#     else:
#         print("static: loading dossiers")
#         data = json.load(open('caches/dossiers.json','r'))
#     for d in data :
#         yield {'idd': d['dossier']['id']}

# @freezer.register_generator
# def keyword():
#     print("generating keywords")
#     if config.dynamic:
#         print("dynamic: setting keywords")
#         data = tools.setkeywords()
#     else:
#         print("static: loading keywords")
#         data = json.load(open('caches/keywords.json','r'))
#     for d in data :
#         yield {'name': d['nameslug']}

# @freezer.register_generator
# def author():
#     print("generating authors")
#     if config.dynamic:
#         print("dynamic: setting authors")
#         data = tools.setauthors()
#     else:
#         print("static: loading authors")
#         data = json.load(open('caches/authors.json','r'))
#     for d in data :
#         yield {'name': d['authorslug']}

@freezer.register_generator
def articlepdf():
    print("generating pdfs")
    dirPath = "build/downloads/"
    # if os.path.exists(dirPath):
    #     print("deleting " + dirPath)
    #     os.rmdir(dirPath)
    if config.dynamic:
        print("dynamic: setting articles")
        data = tools.retrievetags("both")
    else:
        print("static: loading articles")
        data = json.load(open('caches/articles.json','r'))
    
    for article in data :
        try:
            if article['myid'] == '':
                yield {'myid': article['id'] + '.pdf'}
            else:
                print("yielding " + article['myid'])
                yield {'myid': article['myid']}
            # print(os.listdir('build/downloads'))
        except Exception as e:
            print(f"An error occurred with{article['id']}: {e}")
            pass
    for article in data:
        tools.renameFiles(article['myid'], "pdf", dirPath)
        print(os.listdir(dirPath))

# @freezer.register_generator
# def articlexml():
    # print("generating xmls")
    # if config.dynamic:
    #     print("dynamic: setting articles")
    #     data = tools.retrievetags("both")
    # else:
    #     print("static: loading articles")
    #     data = json.load(open('caches/articles.json','r'))
    
    # for article in data :
    #     try:
    #         if article['myid'] == '':
    #             yield {'myid': article['id'] + '.xml'}
    #         else:
    #             print("yielding" + article['myid'])
    #             yield {'myid': article['myid']}
    #         tools.renameFiles(article['myid'], "xml")
    #     except:
    #         print("error with " + article['id'])
    #         pass

if __name__ == '__main__':
    print("freezing")
    
    app.config['FREEZER_DESTINATION_IGNORE'] = 'build/downloads/*'
    freezer.freeze()
