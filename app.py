import streamlit as st
from groq import Groq
from PIL import Image
import os

# --- CONFIGURATION DE L'API ---
client = Groq(api_key="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")

st.set_page_config(page_title="Abirux Interview Coach", page_icon="🎓", layout="wide")

# --- STYLE CSS CORRECTIF ---
st.markdown("""
    <style>
    .main { background-color: #f8faff; }
    
    /* On force une hauteur fixe et un bon cadrage pour toutes les images */
    .stImage img { 
        border-radius: 12px; 
        object-fit: cover; 
        height: 250px !important; 
        width: 100%;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 4.5em;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CHARGEMENT DU LOGO ---
logo_path = "logo.png"
logo_image = None
if os.path.exists(logo_path):
    logo_image = Image.open(logo_path)

# --- INITIALISATION DE LA SESSION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "themes" not in st.session_state:
    st.session_state.themes = None
if "current_theme" not in st.session_state:
    st.session_state.current_theme = None

# --- BARRE LATÉRALE ---
with st.sidebar:
    if logo_image:
        st.image(logo_image, use_container_width=True)
    st.title("⚙️ Configuration")
    niveau = st.selectbox("Niveau du poste", ["Junior", "Intermédiaire", "Senior", "Lead"])
    langue = st.radio("Langue de l'entretien", ["Français", "Anglais"])
    st.divider()
    if st.button("🔄 Réinitialiser la session"):
        st.session_state.clear()
        st.rerun()

# --- ENTÊTE ET DESCRIPTION DU PROJET ---
col_head1, col_head2 = st.columns([1, 5])
with col_head1:
    if logo_image:
        st.image(logo_image, width=90)
with col_head2:
    st.title("Abirux Interview Coach")
    st.markdown(f"""
        ### Bienvenue sur votre simulateur d'entretien intelligent.
        Cette application utilise l'intelligence artificielle pour vous aider à décrocher votre futur job. 
        **Comment ça marche ?** Saisissez l'intitulé de votre poste, choisissez l'un des 6 modules de révision générés 
        automatiquement, et répondez aux questions. L'IA vous donnera un feedback précis, une note et la réponse parfaite.
    """)

st.divider()

# --- ZONE DE SAISIE ---
job_title = st.text_input("🎯 Quel poste préparez-vous ?", placeholder="ex: Data Scientist, Chef de Projet, Développeur...")

# --- AFFICHAGE DES 3 IMAGES (DYNAMIQUE OU ACCUEIL) ---
img_col1, img_col2, img_col3 = st.columns(3)

if job_title:
    # Si un poste est saisi, images liées au métier
    keyword = job_title.replace(' ', ',')
    with img_col1: st.image(f"https://loremflickr.com/400/300/{keyword}?lock=1")
    with img_col2: st.image(f"https://loremflickr.com/400/300/{keyword}?lock=2")
    with img_col3: st.image(f"https://loremflickr.com/400/300/{keyword}?lock=3")
else:
    # Si rien n'est saisi, images de bureau/entretien par défaut
    with img_col1: st.image("https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?q=80&w=400&h=300&fit=crop")
    with img_col2: st.image("https://images.unsplash.com/photo-1521737711867-e3b97375f902?q=80&w=400&h=300&fit=crop")
    with img_col3: st.image("https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?q=80&w=400&h=300&fit=crop")

# --- LOGIQUE DES MODULES ---
if job_title:
    # 1. Génération des thèmes
    if st.session_state.themes is None:
        with st.spinner("✨ Préparation des modules..."):
            prompt_themes = f"Pour un poste de {job_title} ({niveau}), liste 6 thématiques d'entretien très courtes (max 3 mots). Réponds uniquement les thèmes séparés par des virgules."
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt_themes}]
            )
            res = completion.choices[0].message.content.replace(";", ",")
            st.session_state.themes = [t.strip().strip('.') for t in res.split(",")][:6]

    # 2. Affichage des modules
    st.write("### 🛠️ Sélectionnez un module de révision")
    themes = st.session_state.themes
    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)
    all_cols = [c1, c2, c3, c4, c5, c6]
    
    for i, theme in enumerate(themes):
        with all_cols[i]:
            if st.button(f"📌 {theme}", key=f"btn_{i}"):
                st.session_state.current_theme = theme
                with st.spinner("IA en réflexion..."):
                    q_prompt = f"Pose-moi une question d'entretien sur '{theme}' pour le poste de {job_title} en {langue}."
                    q_res = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": q_prompt}]
                    )
                    st.session_state.messages = [{"role": "assistant", "content": q_res.choices[0].message.content}]

    # 3. Zone de Chat
    if st.session_state.current_theme:
        st.divider()
        st.markdown(f"### 💬 Session : `{st.session_state.current_theme}`")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Votre réponse..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Analyse..."):
                    feedback_prompt = f"""
                    Poste : {job_title} | Thème : {st.session_state.current_theme}
                    Réponse candidat : "{prompt}"
                    Structure : Feedback, Note /10, Réponse Idéale, Question Suivante. Langue : {langue}.
                    """
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "system", "content": "Tu es un recruteur expert."},
                                  {"role": "user", "content": feedback_prompt}]
                    )
                    st.markdown(response.choices[0].message.content)
                    st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
else:
    st.info("👋 Bienvenue ! Saisissez votre futur métier pour commencer l'entraînement.")