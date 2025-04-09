import streamlit as st
import feedparser
from datetime import datetime, timedelta
import pandas as pd
import io
from fpdf import FPDF

st.set_page_config(page_title="Revue de presse SIEP", page_icon="📰", layout="wide")

# ---------- RUBRIQUES ET MOTS-CLÉS ----------
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
        "passerelle", "valorisation des acquis", "VAE"
    ]
}

sources_fiables = [
    "rtbf.be", "lesoir.be", "lalibre.be", "lecho.be", "sudpresse.be",
    "forem.be", "actiris.be", "siep.be", "enseignement.be",
    "enseignement.catholique.be", "cfwb.be", "socialsecurity.be",
    "emploi.belgique.be"
]

# ---------- UI ----------
st.title("Revue de presse 📚 - SIEP Liège")
st.markdown(
    "<div style='display: flex; justify-content: flex-end;'>"
    "<a href='mode_emploi.pdf' download>"
    "<button style='background-color:#f1f3f6;padding:0.5rem;border-radius:6px;border:1px solid #d1d1d1;'>"
    "📘 Mode d'emploi + rubriques"
    "</button></a></div>", unsafe_allow_html=True
)

rubrique = st.selectbox("Rubrique", list(rubriques.keys()))
custom_sources_input = st.text_input("Ajouter des sites web supplémentaires à consulter (ex: https://mon-site.be), séparés par des virgules :")
custom_sources = [url.strip().replace("https://", "").replace("http://", "").strip("/") for url in custom_sources_input.split(",") if url.strip()]

col1, col2 = st.columns(2)
start_date = col1.date_input("Date de début", datetime.today() - timedelta(days=30))
end_date = col2.date_input("Date de fin", datetime.today())

custom_keyword = st.text_input("Rechercher un mot-clé personnalisé (optionnel) :")

# ---------- RECHERCHE ----------
def create_rss_url(keyword, start_date, end_date):
    base_url = "https://news.google.com/rss/search?"
    query = f"q={keyword.replace(' ', '+')}+after:{start_date}+before:{end_date}"
    return base_url + query + "&hl=fr&gl=BE&ceid=BE:fr"

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
                "source": link.split('/')[2]
            })
    return articles

if st.button("🔍 Rechercher"):
    keywords = rubriques[rubrique]
    if custom_keyword:
        keywords = [custom_keyword]
    else:
        keywords = rubriques[rubrique]

    all_articles = []
    matched_keywords = []

    for kw in keywords:
        url = create_rss_url(kw, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        articles = get_articles(url, sources_fiables + custom_sources)
        if articles:
            matched_keywords.append(kw)
            for a in articles:
                a["keyword"] = kw
            all_articles.extend(articles)

    if all_articles:
        st.success("Mots-clés ayant donné des résultats : " + ", ".join(matched_keywords))
        search_filter = st.text_input("🔍 Filtrer les articles par mot-clé dans le titre :")

        for article in all_articles:
            if search_filter.lower() in article['title'].lower():
                cols = st.columns([6, 1])
                cols[0].markdown(
                    f"**{article['title']}**  
"
                    f"_{article['source']} - {article['date']}_  
"
                    f"[Lire l'article]({article['link']})"
                )
                if cols[1].button("🗑️ Supprimer", key=article['link']):
                    all_articles.remove(article)

        # Export CSV
        df = pd.DataFrame(all_articles)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Exporter les résultats (CSV)", data=csv, file_name="revue_presse_siep.csv", mime="text/csv", key="download_csv")
    else:
        st.info("Aucun article pertinent trouvé pour cette rubrique et cette période.")