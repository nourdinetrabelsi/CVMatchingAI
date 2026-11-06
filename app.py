"""CVMatchingAI V11 — candidature guidée, état persistant et interface accessible."""
from pathlib import Path
import hashlib
import html
import io
import re
import streamlit as st
import pandas as pd
from docx import Document

from src.backend import analyze, optimize, coach
from src.export_cv import make_docx
from src.llm import check_connection

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="CVMatchingAI | Career Studio", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
:root {color-scheme:light}
html, body, [data-testid="stApp"] {font-family:'DM Sans',Arial,sans-serif; color:#15263c}
[data-testid="stAppViewContainer"], [data-testid="stMain"] {background:#f5f7fb}
[data-testid="stSidebar"] {background:#101e35}
[data-testid="stSidebar"] * {color:#f0f6ff!important}
[data-testid="stSidebar"] [data-testid="stAlert"] * {color:#15324d!important}
[data-testid="stSidebar"] .stButton button {background:#1d3554!important; border:1px solid #375574!important; color:#fff!important; text-align:left; justify-content:flex-start}
[data-testid="stSidebar"] .stButton button:hover {background:#245b6a!important}
[data-testid="stSidebar"] .stButton button[kind="primary"] {background:#0b938c!important}
[data-testid="stHeader"] {background:transparent}
.block-container {max-width:1200px; padding-top:1.8rem; padding-bottom:4rem}
h1,h2,h3,h4 {color:#11263e!important;letter-spacing:-.025em}
h1 {font-weight:800!important}
p,li,label,small {color:#273b53}
.hero {background:linear-gradient(115deg,#11223d 5%,#164b62 70%,#087f83);border-radius:22px;padding:30px 36px;color:#fff;margin-bottom:23px;box-shadow:0 15px 35px #132e4b16}
.hero h1 {color:#fff!important;font-size:2.25rem;line-height:1.2;margin:9px 0}
.hero p {color:#e2f5f7;font-size:1.02rem;max-width:800px;margin:0}
.hero .eyebrow {color:#91f2df;font-size:.78rem;letter-spacing:.16em;font-weight:800}
.section-tag {color:#007e80;font-weight:800;letter-spacing:.11em;font-size:.78rem;margin-bottom:10px}
.stButton>button,.stDownloadButton>button {border-radius:11px!important;min-height:2.85rem!important;font-weight:700!important;color:#15324d!important;border:1px solid #b9cbd9!important;background:#fff!important}
.stButton>button:hover,.stDownloadButton>button:hover {border-color:#087e83!important;background:#e9f8f6!important;color:#075b5f!important}
.stButton>button[kind="primary"],.stDownloadButton>button[kind="primary"] {background:#087e83!important;color:white!important;border:1px solid #087e83!important}
.stButton>button[kind="primary"]:hover,.stDownloadButton>button[kind="primary"]:hover {background:#06676d!important;color:white!important}
.stButton>button:disabled {opacity:.55!important}
[data-testid="stWidgetLabel"] * {color:#19314a!important;opacity:1!important}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] * {color:#fff!important}
textarea,input,[data-testid="stTextArea"] textarea,[data-baseweb="select"]>div {background:#fff!important;color:#142c45!important;-webkit-text-fill-color:#142c45!important;border-radius:10px!important}
[data-testid="stVerticalBlockBorderWrapper"] > div {border-color:#dbe5ee!important;border-radius:17px!important;background:#fff!important}
[data-testid="stMetric"] {background:#fff;border:1px solid #dbe5ee;padding:16px;border-radius:14px}
[data-testid="stMetric"] * {color:#16314b!important;opacity:1!important;-webkit-text-fill-color:#16314b!important}
[data-testid="stMetricValue"] {font-weight:800!important;font-size:1.9rem!important}
[data-testid="stAlert"] {border-radius:12px!important}
[data-testid="stAlert"] * {color:#19324a!important}
.skill {display:inline-block;background:#e2f5f1;color:#065e58;padding:7px 11px;border-radius:8px;margin:3px;font-weight:700;font-size:.86rem}
.skill.gap {background:#fff0d9;color:#87550c}
.cv-paper {background:#fff;color:#1a3048;border:1px solid #d9e4ed;border-top:6px solid #0b8884;box-shadow:0 15px 30px #18344a12;border-radius:6px;padding:34px 42px;min-height:400px;line-height:1.65;white-space:pre-wrap;overflow-wrap:anywhere;font-size:.92rem}
.step-caption {font-size:.84rem;color:#657991}
</style>""", unsafe_allow_html=True)

PAGES = ["01 · Accueil & import", "02 · Analyse de candidature", "03 · CV optimisé", "04 · Plan de formation"]
DEFAULTS = {"cv_text":"", "job_text":"", "cv_label":"Aucun CV", "cv_source_hash":"", "draft_text":"", "draft_signature":"", "plan_text":"", "plan_signature":"", "page":PAGES[0], "consent":False}
for k,v in DEFAULTS.items(): st.session_state.setdefault(k,v)

def secret(name, default=""):
    try: return st.secrets.get(name,default)
    except Exception: return default

def fingerprint():
    return hashlib.sha256((st.session_state.cv_text+'\0'+st.session_state.job_text).encode()).hexdigest()

def set_cv(text, label):
    st.session_state.cv_text = text.strip()
    st.session_state.cv_label = label
    st.session_state.cv_source_hash = hashlib.sha256(text.encode()).hexdigest()
    st.session_state.draft_text = ''
    st.session_state.draft_signature = ''
    st.session_state.plan_text = ''
    st.session_state.plan_signature = ''

def update_cv_editor():
    new = st.session_state.get('_cv_editor','')
    if new != st.session_state.cv_text: set_cv(new,'CV édité')

def update_job_editor():
    st.session_state.job_text = st.session_state.get('_job_editor','')

def navigate(page):
    st.session_state.page=page
    st.rerun()

@st.cache_data(show_spinner=False)
def load_dataset():
    path=ROOT/'data'/'cv_clean.csv'
    return pd.read_csv(path,usecols=['cv_id','clean_text'],low_memory=False).fillna('')

@st.cache_data(show_spinner=False)
def extract_file(filename, raw):
    ext=Path(filename).suffix.lower()
    if ext=='.txt': return raw.decode('utf-8-sig',errors='replace')
    if ext=='.docx':
        doc=Document(io.BytesIO(raw))
        paragraphs=[p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows: paragraphs.append(' | '.join(cell.text for cell in row.cells))
        return '\n'.join(paragraphs)
    if ext=='.pdf':
        import fitz
        with fitz.open(stream=raw,filetype='pdf') as doc: return '\n'.join(p.get_text() for p in doc)
    raise ValueError('Format non pris en charge')

def tags(values, missing=False):
    if not values: st.caption('Aucune compétence reconnue automatiquement.')
    else:
        cls='skill gap' if missing else 'skill'
        st.markdown(''.join(f'<span class="{cls}">{html.escape(str(v))}</span>' for v in values),unsafe_allow_html=True)

def safe_markdown(text):
    st.markdown(text)

key = secret('GROQ_API_KEY', '')
model = secret('GROQ_MODEL','openai/gpt-oss-20b')
if key.startswith(('TA_','REMPLACEZ_','COLLEZ_')): key=''

with st.sidebar:
    st.markdown('## 🎯 CVMatchingAI')
    st.caption('CAREER STUDIO · VERSION 11')
    st.divider()
    st.markdown('**Votre parcours**')
    for idx, page_name in enumerate(PAGES):
        if st.button(page_name, key=f'nav_{idx}',type='primary' if st.session_state.page==page_name else 'secondary',use_container_width=True): navigate(page_name)
    st.divider()
    st.markdown('**Dossier en cours**')
    st.caption('CV : '+('✓ '+st.session_state.cv_label if st.session_state.cv_text else 'Non chargé'))
    st.caption('Offre : '+('✓ Description disponible' if st.session_state.job_text.strip() else 'Non chargée'))
    st.divider()
    st.markdown('**Intelligence artificielle**')
    if key: st.success('Clé Groq trouvée sur le serveur')
    else: st.info('Mode local disponible · configurez Groq pour la génération')
    if st.button('Tester la connexion Groq',disabled=not bool(key),use_container_width=True):
        try:
            with st.spinner('Vérification sans CV...'): check_connection(key,model)
            st.success('Clé valide et modèle accessible')
        except Exception as exc: st.error(str(exc))
    st.checkbox('Autoriser l’envoi de ce CV et de cette offre à Groq',key='consent')
    st.caption('Aucun CV n’est envoyé pendant l’analyse locale. Utilisez des CV anonymisés ou autorisés.')

page=st.session_state.page
st.markdown(f'<div class="hero"><div class="eyebrow">CVMATCHINGAI · {html.escape(page.upper())}</div><h1>Votre prochaine opportunité commence ici.</h1><p>Un seul parcours pour analyser une offre, adapter votre CV et préparer votre montée en compétences.</p></div>',unsafe_allow_html=True)

if page==PAGES[0]:
    st.markdown('<div class="section-tag">ÉTAPE 01 / PRÉPARER LA CANDIDATURE</div>',unsafe_allow_html=True)
    st.subheader('Commençons par votre CV et le poste visé')
    a,b=st.columns(2,gap='large')
    with a:
        with st.container(border=True):
            st.markdown('### ① Votre CV')
            source=st.radio('Comment souhaitez-vous ajouter votre CV ?', ['Importer un fichier','Choisir dans le dataset','Coller un CV'],horizontal=False,key='source_choice')
            if source=='Importer un fichier':
                file=st.file_uploader('CV au format PDF, DOCX ou TXT',type=['pdf','docx','txt'],key='_upload')
                if file is not None:
                    raw=file.getvalue()
                    sig=hashlib.sha256(raw).hexdigest()
                    if sig!=st.session_state.cv_source_hash:
                        try:
                            extracted=extract_file(file.name,raw)
                            if extracted.strip():
                                set_cv(extracted,file.name)
                                st.session_state.cv_source_hash=sig
                                st.rerun()
                            else: st.warning('Aucun texte extractible : un PDF scanné peut nécessiter un OCR.')
                        except Exception as exc: st.error(f'Lecture impossible : {exc}')
            elif source=='Choisir dans le dataset':
                df=load_dataset()
                search=st.text_input('Rechercher un identifiant de CV',placeholder='Exemple : cv (805)')
                ids=df.cv_id.astype(str)
                filtered=ids[ids.str.contains(search,case=False,regex=False)].head(100).tolist() if search else ids.head(100).tolist()
                if filtered:
                    selected=st.selectbox('CV disponibles',filtered)
                    if st.button('Utiliser ce CV',type='primary',use_container_width=True):
                        set_cv(str(df.loc[df.cv_id==selected,'clean_text'].iloc[0]),selected)
                        st.rerun()
                else: st.info('Aucun CV correspondant.')
                st.caption('Les CV du dataset peuvent contenir des données personnelles : n’activez Groq qu’avec une autorisation appropriée.')
            if source=='Coller un CV':
                if '_cv_editor' not in st.session_state: st.session_state['_cv_editor']=st.session_state.cv_text
                st.text_area('Texte du CV',height=220,key='_cv_editor',on_change=update_cv_editor,placeholder='Collez ici le contenu de votre CV...')
                if st.button('Enregistrer ce CV',use_container_width=True):
                    update_cv_editor(); st.rerun()
            if st.session_state.cv_text:
                st.success(f'CV conservé pendant la navigation · {len(st.session_state.cv_text):,} caractères')
                with st.expander('Consulter le CV actuellement chargé'):
                    st.text_area('Aperçu du texte',value=st.session_state.cv_text,height=170,disabled=True,key='_cv_preview')
                if st.button('Retirer le CV actuel',use_container_width=True): set_cv('','Aucun CV');st.session_state.pop('_upload',None);st.session_state.pop('_cv_editor',None);st.rerun()
    with b:
        with st.container(border=True):
            st.markdown('### ② Offre d’emploi')
            st.caption('Copiez une annonce complète avec les missions, technologies et exigences.')
            # The widget key is temporary: the durable value survives Streamlit widget cleanup.
            if '_job_editor' not in st.session_state: st.session_state['_job_editor']=st.session_state.job_text
            st.text_area('Description de l’offre',key='_job_editor',height=270,on_change=update_job_editor,placeholder='Poste : Data Analyst\nMissions : ...\nCompétences requises : Python, SQL, Power BI...')
            if st.button('Enregistrer cette offre',use_container_width=True): update_job_editor();st.rerun()
            if st.session_state.job_text.strip(): st.success('Offre conservée pendant la navigation')
            else: st.caption('Le dataset d’offres fourni ne contient pas de descriptions complètes : collez une annonce réelle.')
    ready=bool(st.session_state.cv_text.strip() and st.session_state.job_text.strip())
    if not ready: st.info('Pour analyser la candidature, ajoutez un CV ET une description d’offre.')
    if st.button('Analyser ma candidature  →',type='primary',disabled=not ready,use_container_width=True):
        update_job_editor() if '_job_editor' in st.session_state else None
        navigate(PAGES[1])

elif page==PAGES[1]:
    st.markdown('<div class="section-tag">ÉTAPE 02 / COMPRENDRE LA COMPATIBILITÉ</div>',unsafe_allow_html=True)
    if not(st.session_state.cv_text.strip() and st.session_state.job_text.strip()):
        st.warning('Votre dossier est incomplet : un CV et une description d’offre sont nécessaires.')
        if st.button('Retourner à l’import',type='primary'): navigate(PAGES[0])
        st.stop()
    report=analyze(st.session_state.cv_text,st.session_state.job_text)
    st.subheader('Ce que votre candidature démontre déjà')
    m1,m2,m3=st.columns(3)
    m1.metric('Compétences repérées dans l’offre',len(report['offer_skills']))
    m2.metric('Compétences communes',len(report['matched_skills']))
    m3.metric('Couverture indicative',f"{report['skill_coverage']:.0%}" if report['skill_coverage'] is not None else 'Non calculable')
    if report['skill_coverage'] is not None: st.progress(max(0,min(1,report['skill_coverage'])))
    else: st.warning('Le dictionnaire NLP ne reconnaît aucune compétence dans cette offre. Le score ne peut pas être calculé.')
    st.caption('Cette couverture mesure uniquement les compétences détectées par le dictionnaire ; ce n’est pas une probabilité de recrutement.')
    left,right=st.columns(2,gap='large')
    with left:
        with st.container(border=True):
            st.markdown('### ✓ Vos points forts')
            tags(report['matched_skills'])
    with right:
        with st.container(border=True):
            st.markdown('### ↗ Compétences à vérifier')
            tags(report['not_detected_skills'],missing=True)
            st.caption('Absentes du CV ≠ non maîtrisées. Vérifiez-les avant de modifier le document.')
    with st.expander('Calculer la similarité sémantique (optionnel)'):
        st.caption('Nécessite un modèle Sentence-Transformers installé séparément. Aucun appel Groq.')
        if st.button('Calculer la similarité'):
            try:
                from src.semantic import compare
                with st.spinner('Calcul des embeddings...'): result=compare(st.session_state.cv_text,st.session_state.job_text,use_embeddings=True)
                st.metric('Similarité cosinus',f"{result['semantic_similarity']:.3f}")
            except Exception as exc: st.error(f'Modèle indisponible : {exc}')
    if st.button('Créer mon CV adapté  →',type='primary',use_container_width=True): navigate(PAGES[2])

elif page==PAGES[2]:
    st.markdown('<div class="section-tag">ÉTAPE 03 / CRÉER UN CV CIBLÉ</div>',unsafe_allow_html=True)
    if not(st.session_state.cv_text.strip() and st.session_state.job_text.strip()):
        st.warning('Ajoutez d’abord votre CV et l’offre cible.')
        if st.button('Retour à l’import',type='primary'): navigate(PAGES[0])
        st.stop()
    st.subheader('Votre CV, mieux présenté et adapté à l’offre')
    st.caption('L’IA peut reformuler les expériences existantes mais ne doit inventer aucune compétence, certification ou expérience.')
    sig=fingerprint()
    if st.button('✦ Générer un CV professionnel avec Groq',type='primary',use_container_width=True,disabled=not(key and st.session_state.consent)):
        if st.session_state.draft_text and st.session_state.draft_signature==sig:
            st.info('Le CV généré pour cette candidature est déjà disponible ci-dessous. Aucun nouvel appel Groq nécessaire.')
        else:
            try:
                with st.spinner('Groq prépare votre CV...'): text=optimize(st.session_state.cv_text,st.session_state.job_text,key,model=model)
                st.session_state.draft_text=text
                st.session_state.draft_signature=sig
                st.session_state['_draft_editor']=text
                st.success('CV généré : relisez toutes les informations avant de le télécharger.')
            except Exception as exc: st.error(str(exc))
    if not key: st.info('Ajoutez une nouvelle clé Groq dans `.streamlit/secrets.toml` pour activer la génération.')
    elif not st.session_state.consent: st.info('Activez le consentement dans la barre latérale avant d’envoyer les textes à Groq.')
    if st.session_state.draft_text and st.session_state.draft_signature==sig:
        st.markdown('### Vérifier et personnaliser le résultat')
        left,right=st.columns([.8,1.2],gap='large')
        with left:
            with st.container(border=True):
                st.markdown('**CV original**')
                st.text_area('Texte source',value=st.session_state.cv_text,height=400,disabled=True,key='_source_view')
        with right:
            with st.container(border=True):
                st.markdown('**CV optimisé — modifiable**')
                if '_draft_editor' not in st.session_state: st.session_state['_draft_editor']=st.session_state.draft_text
                st.text_area('Modifier le contenu',key='_draft_editor',height=400)
                if st.button('Actualiser l’aperçu',use_container_width=True):
                    st.session_state.draft_text=st.session_state['_draft_editor'];st.rerun()
        st.markdown('### Aperçu du document')
        draft=st.session_state.get('_draft_editor',st.session_state.draft_text)
        st.markdown('<div class="cv-paper">'+html.escape(draft[:25000])+'</div>',unsafe_allow_html=True)
        a,b=st.columns(2)
        a.download_button('Télécharger mon CV en DOCX',make_docx(draft,heading=''),file_name='CVMatchingAI_CV_adapte.docx',mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',type='primary',use_container_width=True)
        b.download_button('Télécharger en TXT',draft,file_name='CVMatchingAI_CV_adapte.txt',mime='text/plain',use_container_width=True)
        st.caption('Aperçu textuel : la mise en page DOCX peut varier. Vérifiez le document dans Word avant candidature.')
    else:
        with st.container(border=True):
            st.markdown('### Votre CV optimisé apparaîtra ici')
            st.write('Une fois généré, vous pourrez comparer les deux versions, modifier le texte et télécharger un DOCX éditable.')
            if st.session_state.draft_signature and st.session_state.draft_signature!=sig: st.warning('Le CV ou l’offre a changé : une nouvelle génération est nécessaire.')
    if st.button('Voir mon plan de formation  →',use_container_width=True): navigate(PAGES[3])

else:
    st.markdown('<div class="section-tag">ÉTAPE 04 / PRÉPARER LA PROGRESSION</div>',unsafe_allow_html=True)
    if not(st.session_state.cv_text.strip() and st.session_state.job_text.strip()):
        st.warning('Ajoutez d’abord votre CV et l’offre cible.')
        if st.button('Retour à l’import',type='primary'): navigate(PAGES[0])
        st.stop()
    report=analyze(st.session_state.cv_text,st.session_state.job_text)
    st.subheader('Les compétences à confirmer ou développer')
    tags(report['not_detected_skills'],missing=True)
    st.caption('Les compétences ci-dessus ne sont pas détectées dans le CV ; elles ne sont pas nécessairement absentes de votre expérience.')
    if report['training']:
        for skill,name,url,project in report['training']:
            with st.container(border=True):
                st.markdown('### '+html.escape(name))
                st.markdown(f'**Ressource :** [Consulter le cours]({url})')
                st.markdown('**Projet conseillé :** '+html.escape(project))
    else: st.info('Aucune formation préconfigurée pour les compétences détectées. La bibliothèque de cours est indicative et non exhaustive.')
    sig=fingerprint()
    if st.button('✦ Générer mon parcours personnalisé avec Groq',type='primary',use_container_width=True,disabled=not(key and st.session_state.consent)):
        if st.session_state.plan_text and st.session_state.plan_signature==sig:
            st.info('Le plan est déjà disponible ci-dessous : aucun nouvel appel Groq.')
        else:
            try:
                with st.spinner('Préparation du parcours...'): plan=coach(st.session_state.cv_text,st.session_state.job_text,key,model=model)
                st.session_state.plan_text=plan;st.session_state.plan_signature=sig
            except Exception as exc: st.error(str(exc))
    if st.session_state.plan_text and st.session_state.plan_signature==sig:
        with st.container(border=True): safe_markdown(st.session_state.plan_text)
    st.caption('Vérifiez la disponibilité et les prérequis des ressources proposées.')

st.divider()
st.caption('CVMatchingAI V11 · Assistant à la candidature · Les analyses sont indicatives et les informations générées doivent être vérifiées.')
