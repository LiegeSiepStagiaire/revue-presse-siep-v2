
import streamlit as st
import feedparser
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Revue de presse SIEP", page_icon="📰", layout="wide")

rubriques = {
    "Travail et Insertion Socio-Professionnelle": [
        "emploi", "recherche d’emploi", "législation du travail", "contrat",
        "job étudiant", "insertion socio-professionnelle", "CISP",
        "année citoyenne", "volontariat", "rédaction de CV"
    ],
    "Enseignement de plein exercice : secondaire et supérieur": [
        "études", "enseignement secondaire", "enseignement supérieur", "enseignement qualifiant", "décret",
        "structure scolaire", "organisation des études", "établissement scolaire", "droit scolaire",
        "exclusion scolaire", "recours scolaire", "accès aux études", "coût des études", "bourse d’étude",
        "prêt d’étude", "CPMS", "école de devoirs", "remédiation", "méthode de travail", "aide à la réussite",
        "tutorat", "DASPA", "certification", "choix d’études", "année préparatoire", "journée portes ouvertes",
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
        "droit à l’image", "réseaux sociaux", "nationalité", "institutions belges", "institutions européennes",
        "droits humains", "partis politiques", "participation des jeunes", "mouvements philosophiques",
        "police", "justice", "groupe de pression"
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
    "emploi.belgique.be", "bx1.be", "guide-social.be", "dhnet.be", "jobat.be",
    "lanouvellegazette.be", "references.lesoir.be", "emploi.wallonie.be",
    "enseignement.cfwb.be", "monorientation.be", "volontariat.be",
    "jeminforme.be", "citedesmetiers.be", "onem.be", "solidaris.be"
]

def create_rss_url(keyword, start_date, end_date):
    base_url = "https://news.google.com/rss/search?"
    query = f"q={keyword.replace(' ', '+')}+after:{start_date}+before:{end_date}"
    params = "&hl=fr&gl=BE&ceid=BE:fr"
    return base_url + query + params

def get_articles(rss_url, sources, accept_all=False):
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries:
        link = entry.link
        if accept_all or any(source in link for source in sources):
            articles.append({
                "title": entry.title,
                "link": link,
                "date": entry.published if 'published' in entry else ""
            })
    return articles

st.title("Revue de presse 📚 - SIEP Liège")

rubrique = st.selectbox("Rubrique", list(rubriques.keys()))

colA, colB = st.columns(2)
start_date = colA.date_input("📅 Date de début", datetime.today() - timedelta(days=30))
end_date = colB.date_input("📅 Date de fin", datetime.today())

custom_sources_input = st.text_input("🔗 Ajouter des sites web supplémentaires (ex: https://mon-site.be), séparés par des virgules :")
custom_sources = [url.strip().replace("https://", "").replace("http://", "").strip("/") for url in custom_sources_input.split(",") if url.strip()]
accept_all = st.checkbox("👀 Voir aussi les sources non vérifiées")

if 'article_history' not in st.session_state:
    st.session_state.article_history = []
    st.session_state.deleted_stack = []

if st.button("🔍 Rechercher"):
    total_articles = []
    for keyword in rubriques[rubrique]:
        url = create_rss_url(keyword, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        articles = get_articles(url, sources_fiables + custom_sources, accept_all)
        total_articles.extend(articles)

    seen = set()
    filtered_articles = []
    for article in total_articles:
        key = (article['title'], article['link'])
        if key not in seen:
            seen.add(key)
            filtered_articles.append(article)

    st.session_state.article_history = filtered_articles
    st.session_state.deleted_stack = []

if st.session_state.article_history or st.session_state.article_history == []:
    search_filter = st.text_input("🔍 Filtrer les articles par mot-clé dans le titre :", "")

    for i, article in enumerate(st.session_state.article_history):
        if search_filter.lower() in article['title'].lower():
            cols = st.columns([5, 1, 1])
            cols[0].markdown(f"**{article['title']}**  \n_{article['date']}_  \n🔗 [Lire l'article]({article['link']})")
            if cols[1].button("🗑️ Supprimer", key=f"delete_{i}"):
                st.session_state.deleted_stack.append(article)
                st.session_state.article_history.pop(i)
                st.experimental_rerun()

    col1, col2, col3 = st.columns(3)
    if col1.button("↩️ Revenir en arrière", disabled=not st.session_state.deleted_stack):
        last_deleted = st.session_state.deleted_stack.pop()
        st.session_state.article_history.append(last_deleted)
        st.experimental_rerun()

    df_export = pd.DataFrame(st.session_state.article_history)
    csv = df_export.to_csv(index=False).encode('utf-8')
    col3.download_button("⬇️ Exporter en CSV", data=csv, file_name="revue_presse_siep.csv", mime="text/csv")

if not st.session_state.article_history:
    st.warning("Aucun article pertinent trouvé pour cette rubrique et cette période.")
