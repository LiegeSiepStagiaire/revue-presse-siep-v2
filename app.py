
import streamlit as st
import feedparser
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Revue de presse SIEP", page_icon="📰", layout="wide")

rubriques = {'Travail et Insertion Socio-Professionnelle': ['emploi', 'recherche d’emploi', 'législation du travail', 'contrat', 'job étudiant', 'insertion socio-professionnelle', 'CISP', 'année citoyenne', 'volontariat', 'rédaction de CV'], 'Enseignement de plein exercice : secondaire et supérieur': ['études', 'enseignement secondaire', 'enseignement supérieur', 'enseignement qualifiant', 'décret', 'structure scolaire', 'organisation des études', 'établissement scolaire', 'droit scolaire', 'exclusion scolaire', 'recours scolaire', 'accès aux études', 'coût des études', 'bourse d’étude', 'prêt d’étude', 'CPMS', 'école de devoirs', 'remédiation', 'méthode de travail', 'aide à la réussite', 'tutorat', 'DASPA', 'certification', 'choix d’études', 'année préparatoire', 'journée portes ouvertes', 'passerelle', 'valorisation des acquis (VAE)'], 'Formation': ['formation en alternance', 'CEFA', 'IFAPME', 'EFP', 'jury', 'enseignement à distance', 'horaire réduit', 'alphabétisation', 'promotion sociale', 'formation demandeur d’emploi', 'FOREM', 'ACTIRIS', 'centre de compétence', 'validation des compétences'], 'Protection sociale / aide aux personnes': ['chômage', 'mutuelle', 'aide sociale', 'revenu d’intégration sociale (RIS)', 'allocations familiales', 'financement des études', 'aide à la jeunesse'], 'Vie familiale et affective': ['sexualité', 'planning familial', 'égalité des genres', 'animation GDBD', 'charte égalité'], 'Qualité de vie': ['santé', 'consommation', 'harcèlement', 'sensibilisation', 'logement intergénérationnel', 'kot étudiant', 'contrat de bail', 'transport'], 'Loisirs / vacances': ['sport', 'stage vacances', 'formation animateur', 'centre d’hébergement', 'centre de rencontre'], 'International': ['projet international', 'séjour linguistique', 'stage à l’étranger', 'apprendre les langues', 'bourse internationale', 'test de langue', 'niveau CECRL', 'mobilité européenne'], 'Être acteur dans la société / Institutions et justice': ['citoyenneté', 'droits', 'devoirs', 'engagement', 'implication politique', 'démocratie', 'droit à l’image', 'réseaux sociaux', 'nationalité', 'institutions belges', 'institutions européennes', 'droits humains', 'partis politiques', 'participation des jeunes', 'mouvements philosophiques', 'police', 'justice', 'groupe de pression'], 'Les Métiers': ['orientation métier', 'projet de vie', 'connaissance de soi', 'information métier', 'exploration', 'rencontre professionnelle']}

sources_fiables = [
    "rtbf.be", "lesoir.be", "lalibre.be", "lecho.be", "sudpresse.be",
    "forem.be", "actiris.be", "siep.be", "enseignement.be",
    "enseignement.catholique.be", "cfwb.be", "socialsecurity.be",
    "emploi.belgique.be", "bx1.be", "guide-social.be", "dhnet.be", "jobat.be",
    "lanouvellegazette.be", "references.lesoir.be", "emploi.wallonie.be",
    "enseignement.cfwb.be", "monorientation.be", "volontariat.be",
    "jeminforme.be", "citedesmetiers.be", "onem.be", "solidaris.be",
    "rtlinfo.be", "telesambre.be", "televesdre.be", "vivacite.be",
    "notélé.be", "canalzoom.be", "namurinfo.be", "journal-lavenir.be",
    "lejournaldujeudi.be", "proximus.be", "metrolibre.be"
]

mois_fr = {
    "Jan": "janvier", "Feb": "février", "Mar": "mars", "Apr": "avril",
    "May": "mai", "Jun": "juin", "Jul": "juillet", "Aug": "août",
    "Sep": "septembre", "Oct": "octobre", "Nov": "novembre", "Dec": "décembre"
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
        if accept_all and (not geo_sources or any(src in link for src in geo_sources) or any(src in link for src in sources)):
            if keyword.lower() in title.lower() or keyword.lower() in summary.lower():
                articles.append({
                    "title": title,
                    "link": link,
                    "date": format_date_francaise(entry.published if 'published' in entry else ""),
                    "keyword": keyword
                })
    return articles

st.title("Revue de presse 📚 - SIEP Liège")

rubrique = st.selectbox("Rubrique", list(rubriques.keys()))
col1, col2 = st.columns(2)
start_date = col1.date_input("📅 Date de début", datetime.today() - timedelta(days=30))
end_date = col2.date_input("📅 Date de fin", datetime.today())

custom_sources_input = st.text_input("🔗 Ajouter des sites web supplémentaires (ex: https://mon-site.be), séparés par des virgules :")
custom_sources = [url.strip().replace("https://", "").replace("http://", "").strip("/") for url in custom_sources_input.split(",") if url.strip()]

custom_keyword = st.text_input("📝 (Optionnel) Rechercher un mot-clé personnalisé en plus de ceux de la rubrique :")

# La case pour "sources non vérifiées" est supprimée => toujours True
zone_geo = st.selectbox("Zone géographique ciblée", list(zones_sources_named.keys()))
accept_all = True
geo_sources = zones_sources_named[zone_geo]

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
            cols[0].markdown(f"**{article['title']}**  \n_{article['date']}_  \n🔗 [Lire l'article]({article['link']})")
            if cols[1].button("🗑️ Supprimer", key=f"delete_{i}"):
                st.session_state.deleted_stack.append(article)
                st.session_state.article_history.pop(i)
                st.rerun()

    colA, colB, colC = st.columns(3)
    if colA.button("↩️ Revenir en arrière", disabled=not st.session_state.deleted_stack):
        last_deleted = st.session_state.deleted_stack.pop()
        st.session_state.article_history.append(last_deleted)
        st.rerun()

    df_export = pd.DataFrame(st.session_state.article_history)
    csv = df_export.to_csv(index=False).encode('utf-8')
    colC.download_button("⬇️ Exporter en CSV", data=csv, file_name="revue_presse_siep.csv", mime="text/csv")

if not st.session_state.article_history:
    st.warning("Aucun article pertinent trouvé pour cette rubrique et cette période.")
