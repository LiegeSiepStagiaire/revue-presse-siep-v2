
import streamlit as st
import feedparser
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Revue de presse SIEP (RSS)", page_icon="📰", layout="wide")

rubriques = {'Travail et Insertion Socio-Professionnelle': ['emploi', 'recherche d’emploi', 'législation du travail', 'contrat', 'job étudiant', 'insertion socio-professionnelle', 'CISP', 'année citoyenne', 'volontariat', 'rédaction de CV'], 'Enseignement de plein exercice : secondaire et supérieur': ['études', 'enseignement secondaire', 'enseignement supérieur', 'enseignement qualifiant', 'décret', 'structure scolaire', 'organisation des études', 'établissement scolaire', 'droit scolaire', 'exclusion scolaire', 'recours scolaire', 'accès aux études', 'coût des études', 'bourse d’étude', 'prêt d’étude', 'CPMS', 'école de devoirs', 'remédiation', 'méthode de travail', 'aide à la réussite', 'tutorat', 'DASPA', 'certification', 'choix d’études', 'année préparatoire', 'journée portes ouvertes', 'passerelle', 'valorisation des acquis (VAE)'], 'Formation': ['formation en alternance', 'CEFA', 'IFAPME', 'EFP', 'jury', 'enseignement à distance', 'horaire réduit', 'alphabétisation', 'promotion sociale', 'formation demandeur d’emploi', 'FOREM', 'ACTIRIS', 'centre de compétence', 'validation des compétences'], 'Protection sociale / aide aux personnes': ['chômage', 'mutuelle', 'aide sociale', 'revenu d’intégration sociale (RIS)', 'allocations familiales', 'financement des études', 'aide à la jeunesse'], 'Vie familiale et affective': ['sexualité', 'planning familial', 'égalité des genres', 'animation GDBD', 'charte égalité'], 'Qualité de vie': ['santé', 'consommation', 'harcèlement', 'sensibilisation', 'logement intergénérationnel', 'kot étudiant', 'contrat de bail', 'transport'], 'Loisirs / vacances': ['sport', 'stage vacances', 'formation animateur', 'centre d’hébergement', 'centre de rencontre'], 'International': ['projet international', 'séjour linguistique', 'stage à l’étranger', 'apprendre les langues', 'bourse internationale', 'test de langue', 'niveau CECRL', 'mobilité européenne'], 'Être acteur dans la société / Institutions et justice': ['citoyenneté', 'droits', 'devoirs', 'engagement', 'implication politique', 'démocratie', 'droit à l’image', 'réseaux sociaux', 'nationalité', 'institutions belges', 'institutions européennes', 'droits humains', 'partis politiques', 'participation des jeunes', 'mouvements philosophiques', 'police', 'justice', 'groupe de pression'], 'Les Métiers': ['orientation métier', 'projet de vie', 'connaissance de soi', 'information métier', 'exploration', 'rencontre professionnelle']}
rss_feeds = {'RTBF': 'https://www.rtbf.be/rss', 'Le Soir': 'https://www.lesoir.be/rss/lesoir.xml', 'La Libre': 'https://www.lalibre.be/rss/section/actu.xml', "L'Écho": 'https://www.lecho.be/rss/algemeen.xml', 'Sudinfo': 'https://www.sudinfo.be/rss', 'DH': 'https://www.dhnet.be/rss/dh.xml', 'BX1': 'https://bx1.be/feed/', 'Le Vif': 'https://www.levif.be/rss.xml', 'Actiris': 'https://www.actiris.brussels/fr/rss/news/', 'Le Forem': 'https://www.leforem.be/RSS/actualites.html'}

st.title("Revue de presse 📚 - SIEP Liège (Flux directs)")

rubrique = st.selectbox("Choisissez une rubrique :", list(rubriques.keys()))
custom_keyword = st.text_input("🔎 (Optionnel) Ajouter un mot-clé personnalisé pour affiner la recherche :")
start_date = st.date_input("📅 Date de début", datetime.today())
end_date = st.date_input("📅 Date de fin", datetime.today())

if 'article_history' not in st.session_state:
    st.session_state.article_history = []
    st.session_state.deleted_stack = []

def article_date_valid(published, start, end):
    try:
        article_date = datetime(*published[:6])
        return start <= article_date.date() <= end
    except:
        return True

if st.button("🔍 Rechercher"):
    total_articles = []
    mots_clés = [custom_keyword] if custom_keyword else rubriques[rubrique]
    mots_captés = set()

    for source, url in rss_feeds.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.title
            summary = entry.get("summary", "")
            link = entry.link
            date = entry.get("published_parsed") or entry.get("updated_parsed")
            if not article_date_valid(date, start_date, end_date):
                continue
            for mot in mots_clés:
                if mot.lower() in title.lower() or mot.lower() in summary.lower():
                    mots_captés.add(mot)
                    formatted_date = datetime(*date[:6]).strftime('%d/%m/%Y %H:%M') if date else ""
                    total_articles.append({
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "source": source,
                        "date": formatted_date,
                        "mot_clé": mot
                    })
                    break

    # Supprimer les doublons
    seen = set()
    filtered_articles = []
    for a in total_articles:
        key = (a['title'], a['link'])
        if key not in seen:
            seen.add(key)
            filtered_articles.append(a)

    st.session_state.article_history = filtered_articles
    st.session_state.deleted_stack = []

    if mots_captés:
        st.success("Mots-clés ayant donné des résultats : " + ", ".join(sorted(mots_captés)))
    else:
        st.info("Aucun mot-clé n'a donné de résultat pour cette période.")

if st.session_state.article_history:
    search_filter = st.text_input("🔍 Filtrer les résultats par mot dans le titre :", "")
    for i, article in enumerate(st.session_state.article_history):
        if search_filter.lower() in article['title'].lower():
            cols = st.columns([5, 1, 1])
            cols[0].markdown(f"**{{article['title']}}**  \n_{{article['source']}} - {{article['date']}}_  \n[Lire l'article]({{article['link']}})"){article['source']} - {article['date']}_  
[Lire l'article]({article['link']})")
            if cols[1].button("🗑️ Supprimer", key=f"delete_{i}"):
                st.session_state.deleted_stack.append(article)
                st.session_state.article_history.pop(i)
                st.rerun()

    col1, col2, col3 = st.columns(3)
    if col1.button("↩️ Revenir en arrière", disabled=not st.session_state.deleted_stack):
        last_deleted = st.session_state.deleted_stack.pop()
        st.session_state.article_history.append(last_deleted)
        st.rerun()

    df = pd.DataFrame(st.session_state.article_history)
    csv = df.to_csv(index=False).encode('utf-8')
    col3.download_button("⬇️ Exporter en CSV", data=csv, file_name="revue_presse_siep.csv", mime="text/csv")
else:
    st.info("Aucun article trouvé pour les critères sélectionnés.")
