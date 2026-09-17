"""
Portfolio dynamique — Daniel Joseph SAMBOU
Version 2 : Streamlit + composant React custom + dashboard Nivo (streamlit-elements)
"""

import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from datetime import datetime

from streamlit_elements import elements, mui, nivo, dashboard
from components.mathlab_matrix import mathlab_matrix

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Daniel Joseph SAMBOU — Portfolio",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,700&family=IBM+Plex+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'IBM Plex Sans', system-ui, sans-serif; color: #3A3F55; }
    h1, h2, h3, h4 { font-family: 'Fraunces', Georgia, serif !important; letter-spacing: -0.01em; color: #3A3F55; }
    /* Mode clair verrouillé — pas de bascule automatique en dark. */
    :root { color-scheme: light !important; }
    .stApp { background: #FEFAF3 !important; color-scheme: light !important; }

    .eyebrow {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase;
        color: #FF7A5C; margin-bottom: 6px;
    }
    .project-card {
        padding: 20px; border: 1px solid rgba(58,63,85,0.12);
        border-radius: 6px; background: #FFFFFF; margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(58,63,85,0.05);
    }
    .stack-pill {
        display: inline-block; padding: 3px 10px; margin: 2px 4px 2px 0;
        border: 1px solid rgba(58,63,85,0.18); border-radius: 999px;
        font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #6B7089;
        background: #FBF7EE;
    }
    [data-testid="stMetricValue"] { font-family: 'Fraunces', serif; font-weight: 500; color: #3A3F55; }
    [data-testid="stSidebar"] { background: #F7F1E3; }
    [data-testid="stSidebar"] h1 { font-size: 28px; color: #3A3F55; }

    .hero-name {
        font-family: 'Fraunces', serif; font-size: clamp(48px, 8vw, 96px);
        line-height: 0.92; font-weight: 500; margin: 8px 0; color: #3A3F55;
    }
    .hero-name em { font-style: italic; color: #FF7A5C; }
    .lede {
        font-family: 'Fraunces', serif; font-weight: 300; font-size: 22px;
        line-height: 1.5; max-width: 62ch; color: #4A5068;
    }
    .lede strong { color: #3A3F55; font-weight: 500; }
    .lede em { color: #FF7A5C; font-style: italic; }
    hr { border-color: rgba(58,63,85,0.1) !important; margin: 24px 0 !important; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================
# DATA
# ============================================================

PROJECTS = [
    {"id": "popay-compare", "title": "Popay Compare",
     "sub": "Outil d'audit de paie — comparaison inter-sources",
     "context": "Popay · 2026", "domain": "Paie & Data",
     "stack": ["FastAPI", "React 19 · TS", "Vite", "Tailwind", "SQLite", "PyYAML"],
     "desc": "Cinq tables plates, résolution floue des rubriques, dictionnaire YAML, drill-down.",
     "metrics": [("59", "rubriques"), ("5", "tables"), ("2", "pays")]},
    {"id": "fraud", "title": "Détection de fraude — BEL_AIR",
     "sub": "API de scoring temps réel sur données de comptage électrique",
     "context": "SENELEC · 2024–25", "domain": "Machine Learning",
     "stack": ["Python 3.12", "scikit-learn", "XGBoost", "FastAPI", "pandas"],
     "desc": "Étiquetage par règle physique (courant présent + tension absente), RF & XGBoost.",
     "metrics": [("397 K", "relevés"), ("99,4 %", "F1 max"), ("1", "règle physique")]},
    {"id": "plsql", "title": "Formules PL/SQL multi-pays",
     "sub": "Congés SN, taxation CM, astreinte GA, présence WAVE",
     "context": "Popay · 2026", "domain": "Paie & Data",
     "stack": ["PL/SQL", "Oracle", "SN · CM · GA · BF"],
     "desc": "1/24ᵉ congés SN, correctif de boucle vide, refonte ratio dynamique WAVE.",
     "metrics": [("4", "pays"), ("1", "bug critique"), ("Dyn.", "ratio")]},
    {"id": "mathlab", "title": "MathLab & AnalyseLab",
     "sub": "Laboratoires web de mathématiques",
     "context": "Perso · 2025–26", "domain": "Web & Maths",
     "stack": ["FastAPI", "SymPy", "SciPy", "NetworkX", "KaTeX"],
     "desc": "Neuf modules : tests stats, matrices, géométrie, barycentres, intégrales.",
     "metrics": [("9", "modules"), ("V10", "version"), ("2", "labos")]},
    {"id": "vocal", "title": "Vocal Remover · Desktop",
     "sub": "Séparation de sources audio, cache SHA-256",
     "context": "Perso · 2025–26", "domain": "Desktop & Audio",
     "stack": ["FastAPI", "Demucs", "React · Vite", "WaveSurfer", "PyInstaller"],
     "desc": "Application locale, Demucs configurable, cache SHA-256, import YouTube.",
     "metrics": [("3", "versions"), ("SHA-256", "cache"), ("1-clic", "install")]},
    {"id": "cm2026", "title": "Qualification CM2026 — Sénégal",
     "sub": "Probabilités de qualification, Monte-Carlo + Elo–Poisson",
     "context": "Perso · 2025", "domain": "Machine Learning",
     "stack": ["FastAPI", "NumPy", "Monte-Carlo", "Elo", "Chart.js"],
     "desc": "Simulation Monte-Carlo, recharge live des scores.",
     "metrics": [("10K+", "simulations"), ("Elo–Poisson", "modèle"), ("Live", "MAJ")]},
]

SKILLS_RADAR = [
    {"axe": "Python", "Data & ML": 92, "Paie & PL/SQL": 55, "Web full-stack": 88},
    {"axe": "SQL", "Data & ML": 65, "Paie & PL/SQL": 95, "Web full-stack": 70},
    {"axe": "React/TS", "Data & ML": 50, "Paie & PL/SQL": 60, "Web full-stack": 90},
    {"axe": "FastAPI", "Data & ML": 80, "Paie & PL/SQL": 65, "Web full-stack": 92},
    {"axe": "ML/Stats", "Data & ML": 90, "Paie & PL/SQL": 40, "Web full-stack": 45},
    {"axe": "Data viz", "Data & ML": 85, "Paie & PL/SQL": 60, "Web full-stack": 78},
]

ACTIVITY_2026 = [
    {"mois": "Jan", "Popay": 12, "Perso": 8, "Formation": 4},
    {"mois": "Fév", "Popay": 18, "Perso": 6, "Formation": 3},
    {"mois": "Mar", "Popay": 22, "Perso": 10, "Formation": 5},
    {"mois": "Avr", "Popay": 35, "Perso": 12, "Formation": 2},
    {"mois": "Mai", "Popay": 42, "Perso": 14, "Formation": 2},
    {"mois": "Juin", "Popay": 48, "Perso": 18, "Formation": 3},
    {"mois": "Juil", "Popay": 45, "Perso": 22, "Formation": 4},
    {"mois": "Aoû", "Popay": 40, "Perso": 25, "Formation": 6},
    {"mois": "Sep", "Popay": 44, "Perso": 20, "Formation": 4},
]


# ============================================================
# COMPOSANTS
# ============================================================

def eyebrow(text):
    st.markdown(f'<div class="eyebrow">{text}</div>', unsafe_allow_html=True)


def render_project_card(p):
    st.markdown('<div class="project-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        eyebrow(p["context"] + " · " + p["domain"])
        st.markdown(f"### {p['title']}")
        st.caption(p["sub"])
        st.write(p["desc"])
        st.markdown("".join(f'<span class="stack-pill">{s}</span>' for s in p["stack"]),
                    unsafe_allow_html=True)
    with c2:
        for value, label in p["metrics"]:
            st.metric(label, value)
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PAGES
# ============================================================

def page_home():
    eyebrow("— Dakar · Sénégal · Disponible")
    st.markdown('<div class="hero-name">Daniel Joseph<br>SAMBOU<em>.</em></div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="lede"><strong>Développeur & data scientist.</strong> '
        "Je construis des outils qui rendent la paie, la fraude et les mathématiques "
        "<em>lisibles</em> — des formules PL/SQL qui tournent chaque mois pour des "
        "milliers de bulletins, aux API de détection qui isolent le signal dans "
        "400 000 lignes de comptage électrique.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Projets déployés", "6+")
    c2.metric("Pays paie servis", "4")
    c3.metric("Meilleur F1 fraude", "99,4 %")
    c4.metric("Stack principale", "FastAPI + React")

    st.markdown("---")
    eyebrow("Ce portfolio en une phrase")
    st.markdown("### Streamlit *hébergeant* un composant React custom.")
    st.write(
        "L'app que vous parcourez est écrite en Python (Streamlit), avec deux "
        "couches de composants React embarqués : (a) un composant custom Vite + "
        "TypeScript maison — voir la page **Démo React** — et (b) un dashboard "
        "Nivo via `streamlit-elements` — voir la page **Dashboard Nivo**."
    )


def page_projects():
    eyebrow("Réalisations sélectionnées")
    st.markdown("## Six projets, *trois terrains*.")
    domains = sorted({p["domain"] for p in PROJECTS})
    selected = st.multiselect("Filtrer par domaine", domains, default=domains)
    st.markdown("---")
    for p in PROJECTS:
        if p["domain"] in selected:
            render_project_card(p)


# ---------- Démo React custom ----------

def page_react_demo():
    eyebrow("Démo React custom")
    st.markdown("## MathLab · Module Matrices *en direct*.")
    st.write(
        "Le composant ci-dessous est un **vrai projet React + TypeScript + Vite** "
        "compilé et servi par Streamlit. L'algèbre linéaire est calculée côté "
        "navigateur en TypeScript pur ; les résultats remontent ensuite à Python "
        "via `Streamlit.setComponentValue()`."
    )
    st.markdown("---")

    size = st.radio("Taille de la matrice initiale", [2, 3], index=1,
                    horizontal=True, key="react_size")

    # Le composant React (mode clair verrouillé côté CSS)
    result = mathlab_matrix(size=size, key=f"matrix-{size}")

    st.markdown("---")
    st.markdown("### Retour du composant vers Python")
    st.caption("Les valeurs ci-dessous sont renvoyées par le React à chaque "
               "modification de la matrice — Python peut alors les traiter, les "
               "stocker, ou les injecter dans un autre calcul.")

    if result:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Déterminant", f"{result['determinant']:.3f}")
        c2.metric("Trace", f"{result['trace']:.3f}")
        c3.metric("Rang", result["rank"])
        c4.metric("Puissance k", result["power_k"])

        with st.expander("▸ Voir le JSON complet renvoyé par React"):
            st.json(result)

        with st.expander("▸ Comment ça fonctionne (extrait)"):
            st.code("""
# Python (Streamlit) → déclare le composant
_component_func = components.declare_component(
    "mathlab_matrix", path="./frontend/dist"
)

# React (TypeScript) → renvoie une valeur à Python
Streamlit.setComponentValue({
  matrix, determinant, trace, rank,
  power_k, power_result, inverse, transpose
})

# Python récupère le résultat comme n'importe quel widget
result = mathlab_matrix(size=3, theme="light")
st.metric("Déterminant", result["determinant"])
""", language="python")


# ---------- Dashboard Nivo ----------

def page_dashboard():
    eyebrow("Dashboard Nivo via streamlit-elements")
    st.markdown("## Tableau de bord d'activité *2026*.")
    st.write(
        "Composants Material-UI et charts Nivo, écrits en Python via "
        "`streamlit-elements` — même bibliothèque de charts que Datadog ou Nivo.rocks."
    )
    st.markdown("---")

    layout = [
        # (i, x, y, w, h)
        dashboard.Item("radar", 0, 0, 6, 5),
        dashboard.Item("line", 6, 0, 6, 5),
        dashboard.Item("pie", 0, 5, 4, 5),
        dashboard.Item("bar", 4, 5, 8, 5),
    ]

    palette = {
        "accent": "#FF7A5C", "teal": "#7BC4B8", "gold": "#F2C14E",
        "ink": "#3A3F55", "muted": "#8B90A3",
    }

    with elements("dashboard"):
        with dashboard.Grid(layout, draggableHandle=".drag-handle"):

            # ---- Radar des compétences ----
            with mui.Card(key="radar", sx={"display": "flex", "flexDirection": "column",
                                            "background": "#FFFFFF"}):
                mui.CardHeader(
                    title="Compétences par axe technique",
                    subheader="Radar des domaines de projet",
                    className="drag-handle",
                    sx={"borderBottom": "1px solid rgba(58,63,85,0.1)",
                        "fontFamily": "'Fraunces', serif", "cursor": "move"},
                )
                with mui.Box(sx={"flex": 1, "minHeight": 320}):
                    nivo.Radar(
                        data=SKILLS_RADAR,
                        keys=["Data & ML", "Paie & PL/SQL", "Web full-stack"],
                        indexBy="axe",
                        maxValue=100,
                        margin={"top": 40, "right": 60, "bottom": 40, "left": 60},
                        borderColor={"from": "color"},
                        gridLabelOffset=16,
                        dotSize=8,
                        dotBorderWidth=2,
                        colors=[palette["accent"], palette["teal"], palette["gold"]],
                        theme={
                            "background": "#FFFFFF",
                            "textColor": palette["ink"],
                            "fontFamily": "IBM Plex Sans",
                            "tooltip": {"container": {"background": "#FFFFFF",
                                                       "color": palette["ink"]}},
                        },
                    )

            # ---- Ligne d'activité mensuelle ----
            with mui.Card(key="line", sx={"display": "flex", "flexDirection": "column",
                                           "background": "#FFFFFF"}):
                mui.CardHeader(
                    title="Activité 2026 — commits & tâches par mois",
                    subheader="Popay · Perso · Formation",
                    className="drag-handle",
                    sx={"borderBottom": "1px solid rgba(58,63,85,0.1)", "cursor": "move"},
                )
                with mui.Box(sx={"flex": 1, "minHeight": 320}):
                    line_data = [
                        {"id": series,
                         "data": [{"x": row["mois"], "y": row[series]}
                                  for row in ACTIVITY_2026]}
                        for series in ["Popay", "Perso", "Formation"]
                    ]
                    nivo.Line(
                        data=line_data,
                        margin={"top": 30, "right": 110, "bottom": 50, "left": 50},
                        xScale={"type": "point"},
                        yScale={"type": "linear", "min": 0, "max": "auto"},
                        axisBottom={"legend": "2026", "legendOffset": 36,
                                    "legendPosition": "middle"},
                        axisLeft={"legend": "tâches", "legendOffset": -40,
                                  "legendPosition": "middle"},
                        pointSize=8, pointBorderWidth=2,
                        useMesh=True, enableArea=True, areaOpacity=0.12,
                        curve="monotoneX",
                        colors=[palette["accent"], palette["teal"], palette["gold"]],
                        legends=[{
                            "anchor": "bottom-right", "direction": "column",
                            "translateX": 100, "itemWidth": 80, "itemHeight": 20,
                            "symbolSize": 10, "symbolShape": "circle",
                        }],
                        theme={"background": "#FFFFFF", "textColor": palette["ink"],
                               "fontFamily": "IBM Plex Sans"},
                    )

            # ---- Camembert répartition ----
            with mui.Card(key="pie", sx={"display": "flex", "flexDirection": "column",
                                          "background": "#FFFFFF"}):
                mui.CardHeader(
                    title="Temps par domaine",
                    subheader="Répartition 2026",
                    className="drag-handle",
                    sx={"borderBottom": "1px solid rgba(58,63,85,0.1)", "cursor": "move"},
                )
                with mui.Box(sx={"flex": 1, "minHeight": 320}):
                    nivo.Pie(
                        data=[
                            {"id": "Paie PL/SQL", "value": 42, "color": palette["accent"]},
                            {"id": "Data science", "value": 28, "color": palette["teal"]},
                            {"id": "Web full-stack", "value": 22, "color": palette["gold"]},
                            {"id": "Formation", "value": 8, "color": palette["muted"]},
                        ],
                        margin={"top": 30, "right": 20, "bottom": 30, "left": 20},
                        innerRadius=0.55, padAngle=1, cornerRadius=4,
                        activeOuterRadiusOffset=6,
                        colors={"datum": "data.color"},
                        borderWidth=1,
                        arcLinkLabelsSkipAngle=10,
                        arcLabelsSkipAngle=10,
                        theme={"background": "#FFFFFF", "textColor": palette["ink"],
                               "fontFamily": "IBM Plex Sans"},
                    )

            # ---- Barres empilées langages ----
            with mui.Card(key="bar", sx={"display": "flex", "flexDirection": "column",
                                          "background": "#FFFFFF"}):
                mui.CardHeader(
                    title="Volume par langage — projets 2024-2026",
                    subheader="Estimé en KLoC",
                    className="drag-handle",
                    sx={"borderBottom": "1px solid rgba(58,63,85,0.1)", "cursor": "move"},
                )
                with mui.Box(sx={"flex": 1, "minHeight": 320}):
                    nivo.Bar(
                        data=[
                            {"projet": "MathLab", "Python": 8.2, "TypeScript": 4.5, "PL/SQL": 0},
                            {"projet": "Popay Compare", "Python": 6.8, "TypeScript": 5.1, "PL/SQL": 0.3},
                            {"projet": "Vocal Remover", "Python": 4.1, "TypeScript": 3.2, "PL/SQL": 0},
                            {"projet": "Fraude BEL_AIR", "Python": 3.6, "TypeScript": 0.4, "PL/SQL": 0},
                            {"projet": "CM2026", "Python": 2.1, "TypeScript": 0.8, "PL/SQL": 0},
                            {"projet": "Formules paie", "Python": 0.4, "TypeScript": 0, "PL/SQL": 6.2},
                        ],
                        keys=["Python", "TypeScript", "PL/SQL"],
                        indexBy="projet",
                        margin={"top": 30, "right": 130, "bottom": 60, "left": 50},
                        padding=0.28,
                        colors=[palette["accent"], palette["teal"], palette["gold"]],
                        borderRadius=2,
                        axisBottom={"tickRotation": -18},
                        axisLeft={"legend": "KLoC", "legendOffset": -40,
                                  "legendPosition": "middle"},
                        labelSkipHeight=12,
                        legends=[{
                            "dataFrom": "keys", "anchor": "bottom-right",
                            "direction": "column", "translateX": 120,
                            "itemWidth": 80, "itemHeight": 20,
                            "symbolSize": 10, "symbolShape": "circle",
                        }],
                        theme={"background": "#FFFFFF", "textColor": palette["ink"],
                               "fontFamily": "IBM Plex Sans"},
                    )

    st.caption("💡 Les cartes sont déplaçables et redimensionnables — attrapez "
               "l'en-tête pour les réagencer.")


# ---------- Autres pages (compactes) ----------

def page_experience():
    eyebrow("Parcours professionnel")
    st.markdown("## Trois stages, *trois métiers*.")
    xps = [
        ("Avr — Sep 2026", "Stagiaire — Développement & Data Science",
         "Popay · Plateforme de paie multi-pays (SN, BF, CM, GA)",
         ["Formules PL/SQL pour quatre pays africains.",
          "Contribution full-stack FastAPI + React sur des applis paie/RH.",
          "Analyse des données paie & RH, outillage interne (Popay Compare)."]),
        ("Avr — Mai 2025", "Stagiaire — Agent de consolidation",
         "Sabre GDS Sénégal",
         ["Consolidation des données de réservation.",
          "Contrôle, rapprochement et fiabilisation des flux GDS."]),
        ("Oct — Déc 2024", "Stagiaire — API de détection de fraude",
         "SENELEC · DSI & Direction du Développement Économique et Social",
         ["Conception d'une API de détection de fraude sur comptage électrique.",
          "Préparation des données, prototypage ML, intégration SI."]),
    ]
    for when, role, org, bullets in xps:
        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown(f"**{when}**")
        with c2:
            st.markdown(f"### {role}")
            st.caption(org)
            for b in bullets:
                st.write(f"— {b}")
        st.markdown("---")


def page_contact():
    eyebrow("Contact")
    st.markdown("## Un projet, *une question* ?")
    st.markdown(
        '<div class="lede">Basé à <strong>Dakar</strong>, disponible pour des '
        "missions en <strong>data science, paie & développement full-stack</strong> — "
        "présentiel Sénégal ou distanciel avec les marchés africains que je connais.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### Coordonnées")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("📧 [Mail](mailto:danieljosephsambou@outlook.com)")
        st.markdown("📱 [WhatsApp](https://wa.me/221771450847)")
        st.markdown("📍 [Adresse](https://maps.app.goo.gl/XfjuoJ7UiSRQ6tvy7)")
    with c2:
        st.markdown("💾 [GitHub](https://github.com/danieljosephsambou)")
        st.markdown("🔗 [LinkedIn](https://www.linkedin.com/in/danieljosephsambou)")


# ============================================================
# NAVIGATION
# ============================================================

PAGES = {
    "Accueil": page_home,
    "Projets": page_projects,
    "Démo React": page_react_demo,
    "Dashboard Nivo": page_dashboard,
    "Parcours": page_experience,
    "Contact": page_contact,
}

with st.sidebar:
    st.markdown("# Daniel Joseph *SAMBOU*")
    st.caption("Développeur & Data Scientist · Dakar")
    st.markdown("---")
    if "page" not in st.session_state:
        st.session_state.page = "Accueil"
    for name in PAGES:
        if st.button(name, use_container_width=True,
                     type="primary" if st.session_state.page == name else "secondary"):
            st.session_state.page = name
            st.rerun()
    st.markdown("---")
    st.caption("◆ Portfolio v2 · React + Nivo")
    st.caption(f"Streamlit · Python 3.12 · {datetime.now():%Y}")

PAGES[st.session_state.page]()
