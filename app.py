
import streamlit as st
import feedparser
from datetime import datetime, timedelta
import pandas as pd
import base64

# Configuration
st.set_page_config(page_title="Revue de presse SIEP", page_icon="📰", layout="wide")

# Logo et titre
col1, col2 = st.columns([9, 1])
with col1:
    st.title("Revue de presse 📚 - SIEP Liège")
with col2:
    with open("/mnt/data/Mode_emploi_SIEP_complet.pdf", "rb") as f:
        st.download_button("📘 Mode d'emploi + rubriques", f, file_name="Mode_emploi_SIEP_complet.pdf")

# Données
rubriques = {
    "Travail et Insertion Socio-Professionnelle": [
        "emploi", "recherche d’emploi", "législation du travail", "contrat",
        "job étudiant", "insertion socio-professionnelle", "CISP",
        "année citoyenne", "volontariat", "rédaction de CV"
    ],
    "Enseignement de plein exercice": [
        "études", "enseignement secondaire", "enseignement supérieur", "enseignement qualifiant",
        "décret", "structure scolaire", "organisation des études", "établissement scolaire",
        "droit scolaire", "exclusion scolaire", "recours scolaire", "accès aux études",
        "coût des études", "bourse d’étude", "prêt d’étude", "CPMS", "école de devoirs",
        "remédiation", "méthode de travail", "aide à la réussite", "tutorat", "DASPA",
        "certification", "choix d’études", "année préparatoire", "journée portes ouvertes",
        "passerelle", "valorisation des acquis (VAE)"
    ]
}

sources_fiables = [
    "rtbf.be", "lesoir.be", "lalibre.be", "lecho.be", "sudpresse.be",
    "forem.be", "actiris.be", "siep.be", "enseignement.be",
    "enseignement.catholique.be", "cfwb.be", "socialsecurity.be",
    "emploi.belgique.be"
]

# Fonctions
def create_rss_url(keyword, start_date, end_date):
    base_url = "https://news.google.com/rss/search?"
    query = f"q={keyword.replace(' ', '+')}+after:{start_date}+before:{end_date}"
    params = "&hl=fr&gl=BE&ceid=BE:fr"
    return base_url + query + params

def get_articles(rss_url, additional_sources):
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries:
        link = entry.link
        if any(source in link for source in sources_fiables + additional_sources):
            articles.append({
                "title": entry.title,
                "link": link,
                "date": entry.published if 'published' in entry else "",
                "source": link.split('/')[2]
            })
    return articles

# UI
rubrique = st.selectbox("Rubrique", list(rubriques.keys()))
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Date de début", datetime.today() - timedelta(days=30))
with col2:
    end_date = st.date_input("Date de fin", datetime.today())

custom_sources_input = st.text_input("Ajouter des sites web supplémentaires à consulter (ex: https://mon-site.be), séparés par des virgules :", "")
custom_sources = [url.strip().replace("https://", "").replace("http://", "").strip("/") for url in custom_sources_input.split(",") if url.strip()]
custom_keyword = st.text_input("Rechercher un mot-clé personnalisé (optionnel) :")

if st.button("🔍 Rechercher"):
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    st.subheader(f"Résultats pour la rubrique '{rubrique}' entre {start_str} et {end_str}")

    total_articles = []
    keywords = [custom_keyword] if custom_keyword else rubriques[rubrique]

    for keyword in keywords:
        url = create_rss_url(keyword, start_str, end_str)
        total_articles.extend(get_articles(url, custom_sources))

    seen = set()
    filtered_articles = []
    for article in total_articles:
        key = (article['title'], article['link'])
        if key not in seen:
            seen.add(key)
            filtered_articles.append(article)

    if filtered_articles:
        for article in filtered_articles:
            st.markdown(
                f"**{article['title']}**  
"
                f"_{article['source']} – {article['date']}_  
"
                f"[Lire l'article]({article['link']})"
            )
            st.markdown("---")
    else:
        st.info("Aucun article pertinent trouvé pour cette rubrique et cette période.")
