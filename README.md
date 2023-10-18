# Site Flask pour afficher les articles de PhilLit

## Installation

- créer un environnement virtuel python avec `python -m venv venv` (ou `python3 -m venv venv`)
- activer l'environnement virtuel avec `source venv/bin/activate`
- choisir dans `config.py` le mot clé (tag utilisé sur stylo) et si on veut un site avec ou sans caches
- installer les dépendances avec `pip install -r requirements.txt`
- créer un fichier `env.py` dans lequel rajouter `myToken = `+ votre token stylo
- faire tourner l'application avec `python app.py`
- produire des htmls statiques avec `python build.py`

## Avec make

- créer un environnement virtuel python avec `python -m venv venv`
- activer l'environnement virtuel avec `source venv/bin/activate`
- choisir dans `config.py` le mot clé et si on veut un site avec ou sans caches
- `make install`: installer les dépendances
- `make run`: faire tourner le serveur
- `make build`: produire les htmls statiques


## Caches et build

Fondamentalement le site peux fonctionner de 3 manières différentes:

1. En dynamique. En mettant `True` dans le champ `dynamic` dans  `config.py`. Le site est créé en dynamique (à savoir à chaque fois qu'une page est demandée). C'est cool, car le site affiché correspond à la version actuelle sur Stylo, en temps réel. **Mais c'est très lent!** Car tous les index sont créés en dynamique.
2. Avec des caches. En mettant `False` dans le champ `dynamic` dans  `config.py`. Dans ce cas l'application d'abord récupère tous les fichiers qu'il lui sont nécessaires en json et ensuite elle sert le site en dynamique à partir de ces fichiers. Évidemment c,est beaucoup plus rapide, mais si on change quelque chose sur Stylo, il faut faire tourner à nouveau l'application pour que les fichiers json en local soit régénérés.
3. En statique: avec `python build.py` (ou `make build`). En utilisant le librairie `freeze` toutes les requetes sont faites et génèrent des HTML statiques. Supercool parce que superperenne! Certes, à chaque fois qu'on change quelque chose, il faut régénérer tous les HTML ;) - **attention**: cette fonctionnalité est encore un peu buggy. Il faudra la debugguer en ayant des véritables articles.

## Mot-clé pour publier

L'application parse tous les articles liés au propriétaire du token déclaré dans `env.py`. Elle sélectionne seulement les articles qui ont été tagué sur Stylo avec le tag mis dans `config.py`.

## IDs

Actuellement l'url des articles est:

- si cela existe, l'id tel que déclaré dans le yaml, avec un plit sur `_`. Donc, si l'id est `blabla__01` l'id pour l'application sera `01` et l'url de l'article `articles/01.html`
- si l'id n'est pas renseigné dans le yaml (déconséillé!!): on utilisera l'id de stylo (la clé qu'on a dans l'url de l'article stylo)

## Utiliser l'api stylo

- Installer graphql-playground
- inserer l'url: `https://stylo.huma-num.fr/graphql`
- éditer (en bas) le header en mettant: `{"Authorization": "Bearer votreToken"}`

Maintenant, sur la droite il y a la doc de l'api.

Pour tester des queries, par exemple:

```
query
	{
    articles
    			{title
           _id
            workingVersion{
              md
              yaml
              bib
            }
          }
  }
```

Cette query renvoie la liste de tous les articles avec leur titre, id et le md + yaml + bibtex de la version de travail.

```
query
	{
   tags{_id name {articles{_id title}}}
  }

```

pour avoir la liste des tags et de leur idi et des articles liés.


## Utiliser retrievearticles.py (obsolète)


Actuellement le Flask fait des rêquetes à la volée. Mais j'ai fait un script qui récupère les articles en local et les écrit dans le dossier /sitestylo/articles en les nommant avec l'id renseigné dans le yaml (s'il existe) ou avec l'id article de stylo. Puisque l'id ne semble jamais renseigné (cf #1) c'est l'id stylo qui est utilisé. Pour tester retrievearticles.py, il suffit de: `python retrievearticles.py` (dans l'ennv virtuel évidemment)

