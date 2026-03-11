# Réponses TP2 - Jenkins Pipeline

## Question 1 : Installation Jenkins

**Q2. Quel est le rôle du volume jenkins-data monté sur /var/jenkins_home ?**

Le volume `jenkins-data` permet de persister toutes les données Jenkins (jobs, configurations, plugins, builds, credentials) sur la machine hôte. Sans ce volume, toutes les données seraient perdues à chaque redémarrage ou suppression du conteneur Jenkins.

**Q3. Expliquez pourquoi on monte /var/run/docker.sock dans le conteneur Jenkins.**

`/var/run/docker.sock` est le socket Unix qui permet de communiquer avec le daemon Docker de l'hôte. En le montant dans Jenkins, on permet au conteneur Jenkins d'exécuter des commandes `docker build` et `docker push` directement sur le Docker de la machine hôte, sans avoir à installer un second daemon Docker. C'est la technique Docker-out-of-Docker (DooD).

---

## Question 2 : Jenkinsfile - Compréhension

**Q1. À quoi sert le bloc post { always { } } ?**

Le bloc `post { always { } }` s'exécute systématiquement à la fin du pipeline, que le build ait réussi ou échoué. Il sert ici à nettoyer les conteneurs Docker lancés pendant les tests (`docker compose down -v`), évitant ainsi de laisser des ressources orphelines sur la machine.

**Q2. Différence entre `agent any` et `agent { docker { image 'python:3.11' } }` ?**

- `agent any` : Jenkins exécute le pipeline sur n'importe quel agent disponible (ici le nœud Jenkins lui-même), sans environnement isolé particulier.
- `agent { docker { image 'python:3.11' } }` : Jenkins lance automatiquement un conteneur Python 3.11 et exécute toutes les étapes du pipeline à l'intérieur de ce conteneur, garantissant un environnement reproductible et isolé.

**Q3. Pourquoi le stage Push utilise-t-il `when { branch 'main' }` ?**

Pour éviter de pousser une image Docker vers le registry pour chaque branche de développement. Seul le code validé et mergé sur `main` représente une version stable digne d'être publiée. Cela évite de polluer le registry avec des images de branches feature non finalisées.

**Q4. Que se passe-t-il si --cov-fail-under=70 n'est pas atteint ?**

Si la couverture de code est inférieure à 70%, pytest retourne un code d'erreur non nul. Jenkins interprète ce code d'erreur comme un échec → le stage **Build & Test** échoue → les stages suivants (Push) sont skippés → le pipeline se termine en FAILURE. C'est un Quality Gate intégré directement dans le pipeline.

---

## Question 3 : Premier build Jenkins

**Q2. 20 dernières lignes de la Console Output (Build #5) :**

```
============================== 34 passed in 0.11s ==============================
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Push)
Stage "Push" skipped due to when conditional
[Pipeline] getContext
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Declarative: Post Actions)
[Pipeline] sh
+ docker compose down -v
[Pipeline] echo
Pipeline reussi ! Image : ghcr.io/imrane69120/sentiment-ai:83fed5b
[Pipeline] }
[Pipeline] // stage
[Pipeline] }
[Pipeline] // withEnv
[Pipeline] }
[Pipeline] // withEnv
[Pipeline] }
[Pipeline] // node
[Pipeline] End of Pipeline
Finished: SUCCESS
```

**Q3. Tag attribué à l'image Docker construite :**

`83fed5b` → image taguée : `ghcr.io/imrane69120/sentiment-ai:83fed5b`
Ce tag correspond aux 7 premiers caractères du SHA du dernier commit Git.

**Q5. Second build automatique :**

Oui, le pipeline s'est relancé automatiquement grâce au webhook GitHub configuré (ngrok + GitHub webhook). Le build #5 a été déclenché avec la cause : **"Started by GitHub push by Imrane69120"**, en quelques secondes après le `git push`.

---

## Question 4 : Webhook et déclenchement automatique

**Q1. Le pipeline s'est-il déclenché automatiquement après le push ?**

Oui. Le build #5 a été déclenché automatiquement quelques secondes après le `git push origin main`, avec la cause "Started by GitHub push by Imrane69120", confirmant que le webhook fonctionne correctement.

**Q2. Différence entre Poll SCM et webhook en termes de délai et charge serveur ?**

- **Poll SCM** : Jenkins interroge GitHub toutes les 5 minutes pour vérifier s'il y a de nouveaux commits. Délai pouvant atteindre 5 minutes, et génère des requêtes régulières même s'il n'y a aucun changement → charge inutile sur le serveur.
- **Webhook** : GitHub notifie Jenkins instantanément dès qu'un push est effectué. Délai de quelques secondes, aucune requête inutile → beaucoup plus efficace et réactif.

**Q3. Ce que fait ngrok et pourquoi il est nécessaire en local :**

ngrok crée un tunnel HTTPS public temporaire qui redirige le trafic internet vers un port local (ici 8080). Il est nécessaire car Jenkins tourne en local sur la machine, et GitHub ne peut pas y accéder directement depuis internet — ngrok sert de pont entre les deux.

---

## Questions de Synthèse

### Question A - Architecture Jenkins

**A1. Rôle de chacun des 4 stages :**

- **Checkout** : Récupère le code source depuis GitHub dans le workspace Jenkins.
- **Lint** : Vérifie la qualité syntaxique du code Python avec flake8 (détecte les erreurs de style).
- **Build & Test** : Construit l'image Docker et lance les tests pytest avec vérification de la couverture (≥ 70%).
- **Push** : Pousse l'image versionnée vers le registry ghcr.io (uniquement sur la branche main).

**A2. Qu'est-ce qu'un agent Jenkins ?**

Un agent Jenkins est l'environnement d'exécution où les étapes du pipeline s'exécutent.
- `agent any` : utilise n'importe quel nœud Jenkins disponible, sans isolement particulier.
- `agent { docker { image 'python:3.11' } }` : lance un conteneur Docker dédié pour l'exécution du pipeline, garantissant un environnement totalement isolé et reproductible avec les dépendances exactes.

**A3. Pourquoi withCredentials { } plutôt qu'écrire le token directement ?**

Écrire un token dans le Jenkinsfile l'expose dans Git (historique, forks publics). `withCredentials` injecte les secrets uniquement au moment de l'exécution comme variables d'environnement, les masque dans les logs Jenkins (remplacés par `****`), et permet de commiter le Jenkinsfile dans Git sans risque de sécurité.

---

### Question B - CI/CD et Qualité

**B1. Concept de "fail fast" en CI/CD :**

"Fail fast" signifie que le pipeline doit échouer le plus tôt possible dès qu'une erreur est détectée, sans exécuter les étapes suivantes inutilement. Si le code est mal écrit, c'est le stage **Lint** qui doit échouer en premier (avant même le build), évitant de perdre du temps et des ressources à construire une image qui sera rejetée.

**B2. Pourquoi ne pas pousser une image pour chaque branche feature ?**

Les branches feature contiennent du code en cours de développement, non validé. Pousser une image pour chaque branche polluerait le registry avec des versions instables, consommerait inutilement de l'espace de stockage, et pourrait prêter à confusion sur quelle image est stable et déployable en production.

**B3. Workflow complet git push → Jenkins → Docker Registry :**

1. `git push origin main` → GitHub reçoit le commit
2. GitHub envoie un webhook POST à Jenkins via ngrok
3. Jenkins déclenche le pipeline : Checkout → Lint → Build & Test
4. Jenkins construit l'image Docker et valide les tests (coverage ≥ 70%)
5. Jenkins pousse l'image taguée `sentiment-ai:SHA` et `sentiment-ai:main` vers ghcr.io

---

### Question C - Traçabilité et Versionnement

**C1. Comment retrouver le code source exact d'une image `sentiment-ai:a3f8c12` ?**

Le tag `a3f8c12` correspond aux 7 premiers caractères du SHA Git du commit utilisé pour builder l'image. Il suffit d'exécuter `git checkout a3f8c12` ou `git show a3f8c12` dans le repository pour retrouver exactement le code source correspondant à cette image en production.

**C2. Pourquoi deux tags (:SHA et :main) ?**

- **`:SHA` (ex: `:83fed5b`)** : tag immuable et unique — permet la traçabilité exacte, le rollback vers une version précise, et l'audit. Ne change jamais.
- **`:main`** : tag "flottant" qui pointe toujours vers la dernière version stable de la branche main — pratique pour les déploiements automatiques qui veulent toujours la dernière version sans connaître le SHA exact.
