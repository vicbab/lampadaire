# Procédure d'édition web

## 1. Mise en forme des textes sur Stylo
Voir document sur le Drive.

## 2. Production des PDF

Ouvrir 4 terminaux

Dans le premier:
``cd pandoc-api/pandoc-api``
``make run``

Dans le deuxième:
``cd lampadaire-export``
``make run``

Dans le troisième:
``cd siterevuestylo``
``python app.py``

Dans le quatrième:
``python build_pdf.py``

Une fois que tous les PDF sont générés, on peut générer le reste. Mais avant, il faut changer les URL d'images sur Stylo. [À automatiser! :: TODO](../TODO.md)

## 3. Production du site web
Garder actifs les quatre terminaux.

Dans le quatrième:
``python build_html.py``

## 4. Vérification

Il faut maintenant vérifier que tout est beau sur toutes les pages du site. [À automatiser! :: TODO](../TODO.md)

## 5. Mise en ligne

Si tout est beau, on peut mettre le site à jour.

``firebase login``
``firebase deploy``

Puis, il faut commit et push avec Git.