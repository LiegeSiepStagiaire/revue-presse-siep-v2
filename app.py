
import streamlit as st
import feedparser
from datetime import datetime, timedelta
import pandas as pd

# ---------- CONFIGURATION UI ----------
st.set_page_config(page_title="Revue de presse SIEP", page_icon="📰", layout="wide")

# ---------- RUBRIQUES ----------
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
    ],
    "Formation": [
        "formation en alternance", "CEFA", "IFAPME", "EFP", "jury", "enseignement à distance",
        "horaire réduit", "alphabétisation", "promotion sociale", "formation demandeur d’emploi",
        "FOREM", "ACTIRIS", "centre de compétence", "validation des compétences"
    ],
    "Protection sociale / aide aux personnes": [
        "chômage", "mutuelle", "aide sociale", "revenu d’intégration sociale (RIS)",
        "allocations familiales", "financement des études", "aide à la jeunesse"
    ],
    "Vie familiale et affective": [
        "sexualité", "planning familial", "égalité des genres", "animation GDBD", "charte égalité"
    ],
    "Qualité de vie": [
        "santé", "consommation", "harcèlement", "sensibilisation", "logement intergénérationnel",
        "kot étudiant", "contrat de bail", "transport"
    ],
    "Loisirs / vacances": [
        "sport", "stage vacances", "formation animateur", "centre d’hébergement", "centre de rencontre"
    ],
    "International": [
        "projet international", "séjour linguistique", "stage à l’étranger", "apprendre les langues",
        "bourse internationale", "test de langue", "niveau CECRL", "mobilité européenne"
    ],
    "Être acteur dans la société / Institutions et justice": [
        "citoyenneté", "droits", "devoirs", "engagement", "implication politique", "démocratie",
        "droit à l’image", "réseaux sociaux", "nationalité", "institutions belges",
        "institutions européennes", "droits humains", "partis politiques", "participation des jeunes",
        "mouvements philosophiques", "police", "justice", "groupe de pression"
    ],
    "Les Métiers": [
        "orientation métier", "projet de vie", "connaissance de soi", "information métier",
        "exploration", "rencontre professionnelle"
    ]
}

sources_fiables = [
    "rtbf.be", "lesoir.be", "lalibre.be", "lecho.be", "sudpresse.be",
    "forem.be", "actiris.be", "siep.be", "enseignement.be",
    "enseignement.catholique.be", "cfwb.be", "socialsecurity.be",
    "emploi.belgique.be"
]

# ---------- FONCTIONS ----------
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
                "source": link.split('/')[2] if '//' in link else ""
            })
    return articles

def convert_to_csv(articles):
    df = pd.DataFrame(articles)
    return df.to_csv(index=False, sep=";").encode("utf-8")

# ---------- INTERFACE ----------
st.title("Revue de presse 📚 - SIEP Liège")

col1, col2 = st.columns([4, 1])
with col2:
    with open("Mode_emploi_SIEP_complet.pdf", "rb") as pdf_file:
        st.download_button(
            label="📘 Mode d'emploi + rubriques",
            data=pdf_file,
            file_name="Mode_emploi_SIEP_complet.pdf",
            mime="application/pdf",
            key="help_pdf"
        )

rubrique = st.selectbox("Rubrique", list(rubriques.keys()))

custom_sources_input = st.text_input(
    "Ajouter des sites web supplémentaires à consulter (ex: https://mon-site.be), séparés par des virgules :",
    ""
)
custom_sources = [url.strip().replace("https://", "").replace("http://", "").strip("/") for url in custom_sources_input.split(",") if url.strip()]

today = datetime.today()
def_start = today - timedelta(days=30)
start_date = st.date_input("Date de début", def_start)
end_date = st.date_input("Date de fin", today)

custom_keyword = st.text_input("Rechercher un mot-clé personnalisé (optionnel) :", "")

if st.button("🔍 Rechercher"):
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    st.subheader(f"Résultats pour la rubrique '{rubrique}' entre {start_str} et {end_str}")

    total_articles = []
    search_terms = [custom_keyword] if custom_keyword else rubriques[rubrique]

    for keyword in search_terms:
        url = create_rss_url(keyword, start_str, end_str)
        articles = get_articles(url, custom_sources)
        if articles:
            total_articles.extend(articles)

    if total_articles:
        st.download_button(
            label="📥 Exporter en CSV",
            data=convert_to_csv(total_articles),
            file_name="revue_presse_siep.csv",
            mime="text/csv",
            key="csv_export_button"
        )

        search_filter = st.text_input("🔎 Filtrer les articles par mot-clé dans le titre :", "")
        for article in total_articles:
            if search_filter.lower() in article["title"].lower():
                st.markdown(
                    f"**{article['title']}**  \n"
                )
                st.markdown("---")
    else:
        st.info("Aucun article pertinent trouvé pour cette rubrique et cette période.")
