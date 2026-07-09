import unicodedata
import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    cohen_kappa_score,
    matthews_corrcoef,
)

def pretty_label(value):
    value = str(value).replace("_", " ").strip()
    value = str(value).replace("cao", "ção")
    value = str(value).replace("Publica", "Pública")
    return value.title()

def normalize_text(value, title=False):
    value = str(value).strip().lower()
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("utf-8")
    value = re.sub(r"\s+", " ", value)
    if title:
        value = value.title()
        value = " ".join([w.lower() if len(w) <= 3 else w for w in value.split()])
    return value

def save_figure(fig, fig_dir, name):
    path = fig_dir / f"{name}.png"
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.show()

def save_table(tab, tab_dir, name, index=False):
    path = tab_dir / f"{name}.csv"
    tab.to_csv(path, index=index, encoding="utf-8-sig")
    return path

def create_date_columns(df):
    df["month"] = df["data_abertura"].dt.to_period("M").dt.to_timestamp()
    df["week"] = df["data_abertura"].dt.to_period("W").dt.to_timestamp()
    return df

def load_and_prepare_data(path):
    df = pd.read_csv(path, dtype={"id_chamado": str})
    df["data_abertura"] = pd.to_datetime(df["data_abertura"], errors="coerce")
    df["texto"] = df["texto"].fillna("").astype(str).str.strip()
    df["bairro"] = df["bairro"].astype(str).str.strip()
    df["bairro"] = df["bairro"].map(normalize_text)
    df["canal"] = df["canal"].astype(str).str.strip()
    df["categoria_real"] = df["categoria_real"].astype(str).str.strip()
    df["texto_limpo"] = df["texto"].str.replace(r"\s+", " ", regex=True).str.strip()
    df["tamanho_texto_palavras"] = df["texto"].str.replace(r"\s+", " ", regex=True).str.strip().str.split().str.len()
    df["palavra_count"] = df["texto"].str.split().str.len()
    df["bool_texto_curto"] = df["palavra_count"] <= 5
    df = create_date_columns(df)
    return  df

def calcular_metricas_globais(y_true, y_pred, labels):
    return {
        "Acurácia": accuracy_score(y_true, y_pred),
        "Acurácia Balanceada": balanced_accuracy_score(y_true, y_pred),
        "Precisão Macro": precision_score(y_true, y_pred, labels=labels, average="macro", zero_division=0),
        "Recall Macro": recall_score(y_true, y_pred, labels=labels, average="macro", zero_division=0),
        "F1 Macro": f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0),
        "Precisão Ponderada": precision_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0),
        "Recall Ponderada": recall_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0),
        "F1 Ponderada": f1_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0),
        "Kappa de Cohen": cohen_kappa_score(y_true, y_pred, labels=labels),
        "Coeficiente de Matthews": matthews_corrcoef(y_true, y_pred)
    }

def gerar_amostra_bootstrap_estratificada(df, coluna_estrato, rng):
    indices = []
    for _, grupo in df.groupby(coluna_estrato):
        idx = grupo.index.to_numpy()
        idx_boot = rng.choice(idx, size=len(idx), replace=True)
        indices.append(idx_boot)

    indices = np.concatenate(indices)
    return df.loc[indices].copy()