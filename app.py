
import streamlit as st
import feedparser
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Revue de presse SIEP", page_icon="📰", layout="wide")

rubriques = {
    'Travail et Insertion Socio-Professionnelle': ['emploi', 'recherche d’emploi', 'législation du travail', 'contrat', 'job étudiant', 'insertion socio-professionnelle', 'CISP', 'année citoyenne', 'volontariat', 'rédaction de CV'],
    # autres rubriques...
}

sources_fiables = ["rtbf.be", "lesoir.be", "lalibre.be", "lecho.be", "sudpresse.be"]

mois_fr = {
    "Jan": "janvier", "Feb": "février", "Mar": "mars", "Apr": "avril", "May": "mai",
    "Jun": "juin", "Jul": "juillet", "Aug": "août", "Sep": "septembre", "Oct": "octobre",
    "Nov": "novembre", "Dec": "décembre"
}

jours_fr = {
    "Mon": "lundi", "Tue": "mardi", "Wed": "mercredi", "Thu": "jeudi",
    "Fri": "vendredi", "Sat": "samedi", "Sun": "dimanche"
}

def format_date_francaise(date_str):
    try:
        parts = date_str.split(" ")
        jour = jours_fr.get(parts[0][:3], parts[0])
        num = parts[1]
        mois = mois_fr.get(parts[2], parts[2])
        annee = parts[3]
        heure = parts[4][:5].replace(":", "h")
        return f"{jour} {num} {mois} {annee} à {heure}"
    except:
        return date_str

def create_rss_url(keyword, start_date, end_date):
    base_url = "https://news.google.com/rss/search?"
    query = f"q={keyword.replace(' ', '+')}+after:{start_date}+before:{end_date}"
    params = "&hl=fr&gl=BE&ceid=BE:fr"
    return base_url + query + params

def get_articles(rss_url, keyword, sources, accept_all=True):
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries:
        link = entry.link
        title = entry.title
        summary = entry.get("summary", "")
        if accept_all or any(source in link for source in sources):
            if keyword.lower() in title.lower() or keyword.lower() in summary.lower():
                articles.append({
                    "title": title,
                    "link": link,
                    "date": format_date_francaise(entry.published if 'published' in entry else ""),
                    "keyword": keyword
                })
    return articles

st.title("Revue de presse 📚 - SIEP Liège")

col1, col2 = st.columns([4, 1])
with col2:
    with open("Mode_emploi_SIEP_complet.pdf", "rb") as pdf_file:
        st.download_button(
            label="📘 Mode d'emploi + rubriques",
            data=pdf_file,
            file_name="Mode_emploi_SIEP_complet.pdf",
            mime="application/pdf"
        )

rubrique = st.selectbox("Rubrique", list(rubriques.keys()))
col1, col2 = st.columns(2)
start_date = col1.date_input("📅 Date de début", datetime.today() - timedelta(days=30))
end_date = col2.date_input("📅 Date de fin", datetime.today())

custom_sources_input = st.text_input("🔗 Ajouter des sites web supplémentaires (ex: https://mon-site.be), séparés par des virgules :")
custom_sources = [url.strip().replace("https://", "").replace("http://", "").strip("/") for url in custom_sources_input.split(",") if url.strip()]

custom_keyword = st.text_input("📝 (Optionnel) Rechercher un mot-clé personnalisé en plus de ceux de la rubrique :")

accept_all = True

if 'article_history' not in st.session_state:
    st.session_state.article_history = []
    st.session_state.deleted_stack = []

if st.button("🔍 Rechercher"):
    total_articles = []
    mots_captés = set()
    keywords_to_search = [custom_keyword] if custom_keyword else rubriques[rubrique].copy()
    if custom_keyword:
        keywords_to_search.append(custom_keyword)

    for keyword in keywords_to_search:
        url = create_rss_url(keyword, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        articles = get_articles(url, keyword, sources_fiables + custom_sources, accept_all)
        if articles:
            mots_captés.add(keyword)
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

    if mots_captés:
        st.success("Mots-clés ayant donné des résultats : " + ", ".join(sorted(mots_captés)))
    else:
        st.info("Aucun mot-clé n'a donné de résultat pour cette période.")

if st.session_state.article_history or st.session_state.article_history == []:
    search_filter = st.text_input("🔍 Filtrer les articles par mot-clé dans le titre :", "")
    for i, article in enumerate(st.session_state.article_history):
        if search_filter.lower() in article['title'].lower():
            cols = st.columns([5, 1, 1])
            cols[0].markdown(f"**{article['title']}**  
_{article['date']}_  
🔗 [Lire l'article]({article['link']})")
            if cols[1].button("🗑️ Supprimer", key=f"delete_{i}"):
                st.session_state.deleted_stack.append(article)
                st.session_state.article_history.pop(i)
                st.rerun()

    colA, colB, colC = st.columns(3)
    if colA.button("↩️ Revenir en arrière", disabled=not st.session_state.deleted_stack):
        last_deleted = st.session_state.deleted_stack.pop()
        st.session_state.article_history.append(last_deleted)
        st.rerun()

if not st.session_state.article_history:
    st.warning("Aucun article pertinent trouvé pour cette rubrique et cette période.")
