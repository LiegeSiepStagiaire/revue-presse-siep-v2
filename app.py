
import streamlit as st
import feedparser
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
from PIL import Image
import base64

# --- Configuration de la page ---
st.set_page_config(page_title="Revue de presse SIEP", page_icon="📰", layout="wide")

# --- Chargement du PDF (mode d'emploi) ---
pdf_path = "mode_emploi_siep.pdf"
try:
    with open(pdf_path, "rb") as f:
        st.markdown(
            "<div style='text-align: right;'>"
            + st.download_button(
                label="📘 Mode d'emploi + rubriques",
                data=f,
                file_name="mode_emploi_siep.pdf",
                mime="application/pdf"
            ).html
            + "</div>",
            unsafe_allow_html=True
        )
except FileNotFoundError:
    st.markdown("*Mode d'emploi SIEP (fichier PDF manquant)*")

# --- Rubriques et mots-clés ---
rubriques = {
    "Travail et Insertion Socio-Professionnelle": [
        "emploi", "recherche d’emploi", "législation du travail", "contrat",
        "job étudiant", "insertion socio-professionnelle", "CISP",
        "année citoyenne", "volontariat", "rédaction de CV"
    ]
    # Ajouter d'autres rubriques ici...
}

sources_fiables = [
    "rtbf.be", "lesoir.be", "lalibre.be", "lecho.be", "sudpresse.be",
    "forem.be", "actiris.be", "siep.be", "enseignement.be",
    "enseignement.catholique.be", "cfwb.be", "socialsecurity.be",
    "emploi.belgique.be"
]

# --- Interface principale ---
st.title("Revue de presse 📚 - SIEP Liège")

col1, col2 = st.columns(2)
rubrique = st.selectbox("Rubrique", list(rubriques.keys()))
custom_sources_input = st.text_input("Ajouter des sites web supplémentaires à consulter (ex: https://mon-site.be), séparés par des virgules :", "")
custom_sources = [url.strip().replace("https://", "").replace("http://", "").strip("/") for url in custom_sources_input.split(",") if url.strip()]

with col1:
    start_date = st.date_input("Date de début", datetime.today() - timedelta(days=30))
with col2:
    end_date = st.date_input("Date de fin", datetime.today())

mot_clef_perso = st.text_input("Rechercher un mot-clé personnalisé (optionnel) :")

# --- Fonctions principales ---
def create_rss_url(keyword, start_date, end_date):
    base_url = "https://news.google.com/rss/search?"
    query = f"q={keyword.replace(' ', '+')}+after:{start_date}+before:{end_date}"
    params = "&hl=fr&gl=BE&ceid=BE:fr"
    return base_url + query + params

def get_articles(rss_url, sources):
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries:
        link = entry.link
        if any(src in link for src in sources):
            articles.append({
                "title": entry.title,
                "link": link,
                "date": entry.published if 'published' in entry else "Date inconnue",
                "source": link.split("/")[2]
            })
    return articles

# --- Lancement de la recherche ---
if st.button("🔍 Rechercher"):
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    st.subheader(f"Résultats pour la rubrique '{rubrique}' entre {start_str} et {end_str}")

    keywords = rubriques[rubrique]
    if mot_clef_perso:
        keywords = [mot_clef_perso]

    all_articles = []
    matched_keywords = []

    for keyword in keywords:
        url = create_rss_url(keyword, start_str, end_str)
        articles = get_articles(url, sources_fiables + custom_sources)
        if articles:
            matched_keywords.append(keyword)
        all_articles.extend(articles)

    # Suppression des doublons
    seen = set()
    unique_articles = []
    for article in all_articles:
        key = (article['title'], article['link'])
        if key not in seen:
            seen.add(key)
            unique_articles.append(article)

    # --- Résumé et affichage ---
    if unique_articles:
        df = pd.DataFrame(unique_articles)
        st.download_button("📥 Exporter les articles (CSV)", df.to_csv(index=False).encode("utf-8"), "revue_presse_siep.csv", mime="text/csv")

        for article in unique_articles:
            st.markdown(f"**{article['title']}**  
_{article['source']} - {article['date']}  
[Lire l'article]({article['link']})")
            st.markdown("---")
    else:
        st.info("Aucun article pertinent trouvé pour cette rubrique et cette période.")
