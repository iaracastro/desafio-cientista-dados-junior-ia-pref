import unicodedata
import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from numpy.random import Generator
from pathlib import Path
from typing import Any, Dict, Iterable, Union
from matplotlib.figure import Figure
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    cohen_kappa_score,
    matthews_corrcoef,
)

def pretty_label(value: Any) -> str:
    """Formata valores categóricos para exibição em tabelas e gráficos."""
    value = str(value).replace("_", " ").strip()
    value = value.replace("cao", "ção")
    value = value.replace("publica", "pública")
    value = value.replace("arvore", "árvore")
    return value.title()

def normalize_text(value: Any, title: bool = False) -> str:
    """Normaliza textos removendo acentos, espaços duplicados e padronizando caixa."""
    value = str(value).strip().lower()
    # Remove acentos e sinais diacríticos para padronizar chaves textuais como bairros/categorias.
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("utf-8")
    # Substitui sequências de espaços, tabs ou quebras de linha por um único espaço.
    value = re.sub(r"\s+", " ", value)
    if title:
        value = value.title()
        # Mantém palavras curtas em minúsculas para evitar títulos visualmente artificiais, como "De", "Da", "Do".
        value = " ".join([w.lower() if len(w) <= 3 else w for w in value.split()])
    return value

def save_figure(fig: Figure, fig_dir: Union[str, Path], name: str) -> None:
    """Salva uma figura em PNG com boa resolução e exibe o gráfico."""
    path = fig_dir / f"{name}.png"
    fig.tight_layout() # Ajusta automaticamente margens e espaçamentos antes de salvar.
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.show()

def save_table(tab: pd.DataFrame, tab_dir: Union[str, Path], name: str, index: bool = False) -> Path:
    """Salva uma tabela em CSV e retorna o caminho do arquivo criado."""
    path = tab_dir / f"{name}.csv"
    # utf-8-sig melhora a compatibilidade do CSV com Excel preservando acentos.
    tab.to_csv(path, index=index, encoding="utf-8-sig")
    return path

def create_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Cria colunas temporais auxiliares de mês e semana a partir de data_abertura."""
    df["month"] = df["data_abertura"].dt.to_period("M").dt.to_timestamp()
    df["week"] = df["data_abertura"].dt.to_period("W").dt.to_timestamp()
    return df

def load_and_prepare_data(path: Union[str, Path]) -> pd.DataFrame:
    """Carrega a base de chamados e cria colunas padronizadas para análise."""
    df = pd.read_csv(path, dtype={"id_chamado": str})
    # Converte datas inválidas para NaT, evitando quebra da execução em registros problemáticos
    df["data_abertura"] = pd.to_datetime(df["data_abertura"], errors="coerce")
    # Padroniza campos textuais básicos para reduzir inconsistências de espaços e tipos
    df["texto"] = df["texto"].fillna("").astype(str).str.strip()
    # Normaliza o nome dos bairros para facilitar agrupamentos e evitar duplicidades por acento/caixa
    df["bairro"] = df["bairro"].astype(str).str.strip()
    df["bairro"] = df["bairro"].map(normalize_text)
    df["canal"] = df["canal"].astype(str).str.strip()
    df["categoria_real"] = df["categoria_real"].astype(str).str.strip()
    df["texto_limpo"] = df["texto"].str.replace(r"\s+", " ", regex=True).str.strip()
    # Conta palavras após normalização simples de espaços
    df["tamanho_texto_palavras"] = df["texto"].str.replace(r"\s+", " ", regex=True).str.strip().str.split().str.len()
    df["palavra_count"] = df["texto"].str.split().str.len()
    df["bool_texto_curto"] = df["palavra_count"] <= 5
    df = create_date_columns(df)
    return  df

def calcular_metricas_globais(y_true: Iterable[Any], y_pred: Iterable[Any], labels: Iterable[Any]) -> Dict[str, float]:
    """Calcula métricas globais de classificação para um conjunto de rótulos."""
    return {
        "Acurácia": accuracy_score(y_true, y_pred),
        "Precisão Macro": precision_score(y_true, y_pred, labels=labels, average="macro", zero_division=0),
        "Recall Macro": recall_score(y_true, y_pred, labels=labels, average="macro", zero_division=0),
        "F1 Macro": f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0),
        "Precisão Ponderada": precision_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0),
        "Recall Ponderada": recall_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0),
        "F1 Ponderada": f1_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0),
        "Kappa de Cohen": cohen_kappa_score(y_true, y_pred, labels=labels),
        "Coeficiente de Matthews": matthews_corrcoef(y_true, y_pred)
    }

def gerar_amostra_bootstrap_estratificada(df: pd.DataFrame, coluna_estrato: str, rng: Generator) -> pd.DataFrame:
    """Gera uma amostra bootstrap preservando o tamanho de cada estrato."""
    indices = []
    # Reamostra cada estrato separadamente para manter a composição da variável de estratificação.
    for _, grupo in df.groupby(coluna_estrato):
        idx = grupo.index.to_numpy()
        idx_boot = rng.choice(idx, size=len(idx), replace=True)
        indices.append(idx_boot)

    # Junta os índices reamostrados de todos os estratos em um único vetor.
    indices = np.concatenate(indices)
    return df.loc[indices].copy()