import csv
import math
import re
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def process_aria_label(aria_label):
    """Convertit 'Note : x sur 5' en un nombre flottant."""
    match = re.search(r"(\d+(?:,\d+)?)", aria_label)
    if match:
        return float(match.group(1).replace(",", "."))
    return "Non disponible"


def process_annexe2(date_text):
    """Convertit les dates relatives (ex. 'il y a 2 mois') en format JJ/MM/AA."""
    now = datetime.now()

    if "il y a" in date_text:
        # Gérer les semaines
        if "semaines" in date_text or "semaine" in date_text:
    # Vérifier si "une" ou un chiffre est mentionné
            if "une" in date_text or "un" in date_text:
                weeks_ago = 1
            else:
                weeks_ago = int(re.search(r"(\d+)", date_text).group())
            target_date = now - timedelta(weeks=weeks_ago)
            return target_date.strftime("%d/%m/%y")

        elif "jours" in date_text or "jour" in date_text:
            # Vérifier si "une" ou un chiffre est mentionné
            if "une" in date_text or "un" in date_text:
                days_ago = 1
            else:
                days_ago = int(re.search(r"(\d+)", date_text).group())
            target_date = now - timedelta(days=days_ago)
            return target_date.strftime("%d/%m/%y")

        elif "mois" in date_text or "mois" in date_text:
            # Vérifier si "un" ou "une" est mentionné
            if "une" in date_text or "un" in date_text:
                months_ago = 1
            else:
                months_ago = int(re.search(r"(\d+)", date_text).group())
            target_date = now - timedelta(days=30 * months_ago)
            return target_date.strftime("%d/%m/%y")

        
        # Gérer "un an"
        elif "un an" in date_text:
            target_date = now.replace(year=now.year - 1, month=1, day=1)
            return target_date.strftime("%d/%m/%y")
        
        # Gérer "année" et "ans"
        elif "année" in date_text or "ans" in date_text:
            years_ago = int(re.search(r"(\d+)", date_text).group())
            target_date = now.replace(year=now.year - years_ago, month=1, day=1)
            return target_date.strftime("%d/%m/%y")

    # Retourner la date originale si aucune correspondance
    return date_text.strip()


def clean_comment(comment_text):
    """Supprime les blocs de notes dans les commentaires."""
    # Expression régulière pour détecter les blocs comme 'Cuisine : x/5  |  Service : x/5  |  Ambiance : x/5'
    pattern = r"Cuisine\s*:\s*\d+/\d+\s*\|\s*Service\s*:\s*\d+/\d+\s*\|\s*Ambiance\s*:\s*\d+/\d+"
    # Remplace ces blocs par une chaîne vide
    return re.sub(pattern, "", comment_text).strip()


def scroll_and_scrape(driver, trigger_class, item_class, link_class, review_class, annexe1_class, annexe2_class, aria_class, iterations=10):
    """
    Scroller toute la page, cliquer sur les balises <a> et scraper les données visibles.
    """
    scraped_data = []  # Liste pour stocker les données combinées
    wait = WebDriverWait(driver, 10)

    # Cliquer sur l'élément avec la classe trigger_class pour activer le contenu
    trigger_element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, trigger_class)))
    trigger_element.click()
    time.sleep(2)

    # Étape 1 : Scroller toute la page
    print("Scrolling through the page...")
    for i in range(iterations):
        print(f"Scroll iteration {i+1}/{iterations}")
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.CONTROL + Keys.END)
        time.sleep(2)  # Attendre que le contenu charge

    # Étape 2 : Collecter toutes les balises <a> après le scroll
    body.send_keys(Keys.CONTROL + Keys.UP)
    time.sleep(2)
    print("Collecting all clickable <a> elements...")
    link_elements = driver.find_elements(By.CLASS_NAME, link_class)
    
    item_count = len(driver.find_elements(By.CLASS_NAME, item_class))
    print(f"Nombre d'éléments avec la classe '{item_class}' trouvés : {item_count}")

    # Étape 3 : Cliquer sur chaque balise <a>
    for link in link_elements:
        try:
            link.click()
            time.sleep(1)  # Petite pause après chaque clic
        except Exception as e:
            print(f"Erreur lors du clic sur une balise <a> : {e}")

    # Étape 4 : Scraper les données des éléments restants
    body.send_keys(Keys.CONTROL + Keys.UP)
    time.sleep(2)
    print("Scraping the visible elements...")
    items = driver.find_elements(By.CLASS_NAME, item_class)
    
    item_count = len(driver.find_elements(By.CLASS_NAME, item_class))
    print(f"Nombre d'éléments avec la classe '{item_class}' trouvés : {item_count}")
    
    for item in items:
        try:
            # Scraper le commentaire
            try:
                review_element = item.find_element(By.CLASS_NAME, review_class)
                comment_text = clean_comment(review_element.text.strip())
            except Exception as e:
                print(f"Erreur lors du scraping de 'Comment' : {e}")
                comment_text = ""

            # Scraper la note (aria-label)
            try:
                aria_element = item.find_element(By.CLASS_NAME, aria_class)
                aria_label = process_aria_label(aria_element.get_attribute("aria-label"))
            except Exception as e:
                print(f"Erreur lors du scraping de 'Note' : {e}")
                aria_label = "Non disponible"

            # Scraper Nom
            try:
                annexe1_element = item.find_element(By.CLASS_NAME, annexe1_class)
                annexe1_text = annexe1_element.text.strip() if annexe1_element.text.strip() else "Non disponible"
            except Exception as e:
                print(f"Erreur lors du scraping de 'Nom' : {e}")
                annexe1_text = "Non disponible"

            # Scraper Date
            try:
                annexe2_element = item.find_element(By.CLASS_NAME, annexe2_class)
                annexe2_text = process_annexe2(annexe2_element.text.strip())
            except Exception as e:
                print(f"Erreur lors du scraping de 'Date' : {e}")
                annexe2_text = "Non disponible"

            # Ajouter les données à la liste
            scraped_data.append([comment_text, aria_label, annexe1_text, annexe2_text])

        except Exception as e:
            print(f"Erreur lors de la récupération d'un élément : {e}")

    return scraped_data


# Initialisation du navigateur
driver = webdriver.Chrome()

business_raw = "Restaurant Istanbul"
business_url = business_raw.replace(" ", "+")

town_raw = "ivry"
town_url = town_raw.replace(" ", "+")

try:
    driver.get(f"https://www.google.com/search?q={business_url}+{town_url}")
    wait = WebDriverWait(driver, 10)

    # Accepter les cookies
    try:
        button_cookie = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='QS5gu sy4vM']")))
        button_cookie.click()
        print('Cookies accepted')
        time.sleep(2)
    except Exception as e:
        print(f"Pas de bouton cookies trouvé : {e}")

    # Calcul du nombre de pages à scroller
    div_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hqzQac")))
    raw_reviews = div_element.text
    cleaned_reviews = re.sub(r"[^\d]", "", raw_reviews)
    nb_reviews = int(cleaned_reviews)
    page_scroll = math.ceil(nb_reviews / 10)

    print('Nombre de reviews :', nb_reviews)
    print('Nombre de pages scrollées :', page_scroll)

    # Naviguer vers les reviews
    button_reviews = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='hqzQac']")))
    button_reviews.click()
    time.sleep(5)
    
    # On trouve la balise correspondant aux avis Google 
    buttons = driver.find_elements(By.XPATH, "//span[@class='xTA1xd SewVgb']")
    # Puis on parcours chaque élément trouvé
    for button in buttons:
        # Vérifier si le contenu du texte est "Google"
        if button.text.strip() == "Google":
            # Cliquer sur le bouton si la condition est remplie
            button.click()
            print('Bouton "More" cliqué')
            time.sleep(5)
            break  # Sortir de la boucle après avoir cliqué sur le bouton correspondant
    else:
        print("Aucun bouton avec le texte 'Google' trouvé.")

    # Scraper les données
    all_data = scroll_and_scrape(
        driver,
        trigger_class="p7f0Nd",
        item_class="bwb7ce",
        link_class="MtCSLb",
        review_class="OA1nbd",
        annexe1_class="Vpc5Fe",
        annexe2_class="y3Ibjb",
        aria_class="dHX2k",
        iterations=page_scroll
    )

    # Export
    file_name = f'comments_{business_raw.replace(" ", "_")}_{town_raw.replace(" ", "_")}'
    with open(f'./comments_{file_name}.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Business', 'Town', 'Comment', 'Rate', 'Name', 'Date'])
        for row in all_data:
            writer.writerow([business_raw, town_raw, *row])

    print(f"{len(all_data)} commentaires enregistrés dans comments.csv")

finally:
    driver.quit()
