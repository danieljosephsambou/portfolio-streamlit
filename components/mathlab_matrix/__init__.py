"""
Wrapper Python pour le composant React MathLab Matrix.

En développement (npm run dev sur le port 5173) :
    _RELEASE = False
En production (après npm run build, sert le dossier dist/) :
    _RELEASE = True
"""
import os
import streamlit.components.v1 as components

_RELEASE = True  # Passez à False pour développer le React à chaud

if _RELEASE:
    _build_dir = os.path.join(os.path.dirname(__file__), "frontend", "dist")
    _component_func = components.declare_component(
        "mathlab_matrix", path=_build_dir
    )
else:
    _component_func = components.declare_component(
        "mathlab_matrix", url="http://localhost:5173"
    )


def mathlab_matrix(
    initial_matrix=None,
    size: int = 3,
    theme: str = "light",
    key: str | None = None,
):
    """
    Affiche le composant React MathLab Matrix et retourne les opérations
    calculées côté client.

    Paramètres
    ----------
    initial_matrix : list[list[float]] | None
        Matrice initiale. Si None, une matrice identité de taille `size`
        est utilisée.
    size : int
        Taille de la matrice (2 ou 3).
    theme : str
        "light" ou "dark".
    key : str | None
        Clé unique Streamlit.

    Retour
    ------
    dict
        {
            "matrix": [[...], ...],
            "determinant": float,
            "trace": float,
            "rank": int,
            "power_k": int,
            "power_result": [[...], ...],
            "inverse": [[...], ...] | None,
            "transpose": [[...], ...],
        }
    """
    if initial_matrix is None:
        initial_matrix = [
            [1.0 if i == j else 0.0 for j in range(size)] for i in range(size)
        ]
    default = {
        "matrix": initial_matrix,
        "determinant": 1.0,
        "trace": float(size),
        "rank": size,
        "power_k": 2,
        "power_result": initial_matrix,
        "inverse": initial_matrix,
        "transpose": initial_matrix,
    }
    return _component_func(
        initial_matrix=initial_matrix,
        size=size,
        theme=theme,
        default=default,
        key=key,
    )
