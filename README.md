# Portfolio dynamique v2 — Streamlit + React + Nivo

Portfolio interactif construit sur trois couches :

- **Streamlit** (Python) — squelette, navigation, contenu textuel
- **Composant React custom** (Vite + TypeScript) — le module *MathLab Matrix*, compilé et embarqué comme composant Streamlit natif, avec communication bidirectionnelle
- **streamlit-elements + Nivo** — dashboard drag-and-drop avec charts Nivo (radar, ligne, pie, barres empilées), écrit en Python

## Structure du dépôt

```
streamlit_portfolio_v2/
├── app.py                              # Application Streamlit (6 pages)
├── requirements.txt                    # Dépendances Python
├── README.md                           # Ce fichier
└── components/
    └── mathlab_matrix/
        ├── __init__.py                 # Wrapper Python du composant
        └── frontend/
            ├── package.json            # deps npm
            ├── vite.config.ts          # config Vite
            ├── tsconfig.json           # config TypeScript
            ├── index.html
            └── src/
                ├── main.tsx            # entry point React
                ├── MatrixLab.tsx       # le composant React
                └── styles.css          # design tokens & mise en forme
```

## Installation & lancement

### Prérequis

- Python 3.12
- Node.js 18+ et npm
- (Recommandé) un venv Python dédié — voir plus bas

### 1) Compiler le composant React (une seule fois)

```bash
cd components/mathlab_matrix/frontend
npm install
npm run build
cd ../../..
```

Cela produit `components/mathlab_matrix/frontend/dist/` que Python sert
automatiquement.

### 2) Installer les dépendances Python

**Fortement recommandé — utiliser un venv dédié pour éviter les conflits
Starlette avec vos autres projets FastAPI :**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# ou : source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 3) Lancer l'app

```bash
streamlit run app.py
```

Ouvrez http://localhost:8501.

## Développer le composant React à chaud

Pendant que vous itérez sur le React (hot-reload Vite) :

1. Ouvrez `components/mathlab_matrix/__init__.py`
2. Passez `_RELEASE = False`
3. Dans un premier terminal :
   ```bash
   cd components/mathlab_matrix/frontend
   npm run dev
   ```
4. Dans un second terminal, à la racine :
   ```bash
   streamlit run app.py
   ```

Vite sert le composant sur `http://localhost:5173` avec hot-reload, et
Streamlit le pointe automatiquement.

Une fois satisfait : `npm run build`, remettez `_RELEASE = True`, commitez.

## Les 6 pages

| Page | Contenu |
|------|---------|
| **Accueil** | Nom, pitch, KPIs |
| **Projets** | Les 6 réalisations, filtrables par domaine |
| **Démo React** ⭐ | Composant Vite/TS custom — calcul déterminant, inverse, puissance, transposée, rang, en temps réel. Communication bidirectionnelle Python ↔ React |
| **Dashboard Nivo** ⭐ | Radar compétences, ligne d'activité, pie répartition, barres langages — cartes drag-and-drop |
| **Parcours** | Les 3 stages |
| **Contact** | Coordonnées |

## Déploiement sur Streamlit Community Cloud

1. Poussez le dépôt sur GitHub, **en incluant `components/mathlab_matrix/frontend/dist/`**
   (ne pas ignorer ce dossier — c'est ce que Streamlit sert en prod).
   Alternative : ajoutez une étape de build dans `.streamlit/packages.txt` +
   un script `postinstall`, mais le plus simple reste de committer `dist/`.
2. Sur https://share.streamlit.io → **New app** → sélectionnez le repo → `app.py`.
3. Deploy. L'app est en ligne en 2-3 minutes.

**Attention Streamlit Cloud :** l'environnement ne pré-installe pas Node.
Si vous voulez que le build se fasse côté cloud, ajoutez `.streamlit/prebuild.sh` :

```bash
#!/bin/bash
cd components/mathlab_matrix/frontend
npm install
npm run build
```

Plus simple : buildez en local, commitez `dist/`.

## Comment ça marche — la communication Python ↔ React

**Python déclare le composant :**
```python
_component_func = components.declare_component(
    "mathlab_matrix",
    path="./frontend/dist",
)
```

**React envoie une valeur à Python :**
```tsx
Streamlit.setComponentValue({
  matrix, determinant, trace, rank,
  power_k, power_result, inverse, transpose
})
```

**Python récupère la valeur comme un widget classique :**
```python
result = mathlab_matrix(size=3, theme="light")
st.metric("Déterminant", result["determinant"])
```

Chaque `setComponentValue` déclenche un rerun Streamlit. C'est exactement ce
qui fait fonctionner `streamlit-aggrid`, `streamlit-webrtc`, et les autres
composants tiers de l'écosystème.

## Ajouter d'autres composants React

Répétez la même structure pour n'importe quelle démo :

```
components/
├── mathlab_matrix/       # matrices (livré)
├── popay_compare_mini/   # à faire — mini comparateur de bulletins
└── fraude_scatter/       # à faire — scatter D3 des détections
```

Chacun a son `__init__.py` Python et son dossier `frontend/` Vite + TS.

## Notes

- Contenu personnel — Daniel Joseph Sambou, 2026
- Palette et typographie inspirées de vos projets MathLab / Popay Compare
