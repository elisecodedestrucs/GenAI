# GEN AI

## 1- SCRAPPING 

## Description
Ce projet permet de scraper les avis Google pour un établissement spécifique dans une ville donnée. Les informations récupérées incluent les commentaires, les notes, les noms des utilisateurs, et les dates des avis. Le script utilise Selenium pour naviguer sur les pages et interagir avec les éléments dynamiques.

---

## Prérequis

### Installation des dépendances

Depuis le terminal, commencez par cloner le projet et installer les dépendances listées dans le fichier `requirements.txt` avec les commandes suivants :
   ```bash
git clone https://github.com/yannamer/GenAI.git
  ```
  ```bash
cd 'lechemindufichier\GenAI'
  ```
  ```bash
pip install -r requirements.txt
  ```
Cela installera les package necessaires.
Assurez-vous également que Google Chrome est installé.

---

## Utilisation

### Input
Une fois le script lancé, celui-ci va demander deux entrées dans le terminal :
1. **Nom de l'entreprise (`business_raw`)** : Nom de l'établissement à rechercher (ex: Albert school).
2. **Ville (`town_raw`)** : Ville où se trouve l'établissement.

Ces deux informations sont combinées pour construire l'URL de recherche Google. Etant une recherche Google, une légère faute d'orthographe est admise.

### Étapes du script
1. **Lancement du navigateur** : Le script utilise Selenium pour ouvrir Google Chrome.
2. **Recherche de l'établissement** : L'URL de recherche est générée à partir des entrées utilisateur.
3. **Navigation vers les avis** :
   - Le script accepte les cookies si nécessaire.
   - Il clique sur les avis Google pour afficher tous les commentaires disponibles.
4. **Défilement** :
   - Le script descend automatiquement en bas de la page pour charger tous les avis et éviter d'éventuels bug et gagner en fluidité.
   - Ensuite, il remonte par étapes tout en scrappant les données visibles.
5. **Scraping des données** :
   - Récupération des commentaires.
   - Extraction des notes des utilisateurs.
   - Récupération des noms des utilisateurs.
   - Conversion des dates des avis au format JJ/MM/AA.
6. **Suppression des doublons** : Les doublons sont supprimés en se basant sur la colonne `Nom` au cas où un utilisateur ai eu un bug et ai mis deux fois le même avis ou note.
7. **Export des données** :
   - Les données sont sauvegardées dans un fichier CSV nommé `<Nom_Entreprise>_<Ville>.csv` dans le dossier `./Comments`.

---

### Output
Le fichier CSV généré contient les colonnes suivantes :
- **Business** : Nom de l'établissement.
- **Town** : Ville.
- **Comment** : Texte du commentaire.
- **Rate** : Note donnée par l'utilisateur.
- **Name** : Nom de l'utilisateur.
- **Date** : Date de l'avis.
