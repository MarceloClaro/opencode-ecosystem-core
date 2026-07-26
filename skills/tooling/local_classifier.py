#!/usr/bin/env python3
"""
LocalClassifier — Classificação de Texto Local (sem LLM)
===========================================================
Substituto de chamadas Ollama/OpenAI para classificação de texto.

Usa TF-IDF + LogisticRegression (sklearn) como padrão,
com fallback para regras textuais quando o modelo não está treinado.

Uso:
    from skills.tooling.local_classifier import LocalClassifier
    clf = LocalClassifier()
    clf.fit(texts, labels)
    result = clf.predict("texto para classificar")
"""

from __future__ import annotations

import json
import re
import time
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Classificadores disponíveis (tentativa de import)
__all__ = ["LocalClassifier", "get_classifier"]


class LocalClassifier:
    """
    Classificador de texto local determinístico.
    Estratégias em cascata:
    1. Regras textuais (regex)
    2. Modelo TF-IDF + LogisticRegression
    3. Similaridade por cosseno com exemplos
    """

    def __init__(self, model_dir: Optional[str] = None, add_default_rules: bool = True):
        self.model_dir = Path(model_dir) if model_dir else (
            Path.home() / ".opencode" / "classifiers"
        )
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self._pipeline: Optional[Pipeline] = None
        self._rules: list = []
        self._label_map: Dict[str, int] = {}
        self._reverse_map: Dict[int, str] = {}
        self._is_fitted = False
        self._threshold = 0.15
        self.stats = {
            "predictions": 0,
            "rule_matches": 0,
            "model_matches": 0,
            "avg_ms": 0.0,
        }

        if add_default_rules:
            self._add_default_rules()

    def _add_default_rules(self):
        """Adiciona regras padrão para classificação sem LLM."""
        self.add_rule(r"(sci.?hub|doi|paper|artigo|download.*pdf)", "download_paper", 0.95)
        self.add_rule(r"(biblioteca|pacote|lib|pypi|pip|pacote|python.*library)", "pypi_search", 0.95)
        self.add_rule(r"(deploy|produção|produção|subir|servidor|CI|CD)", "devops", 0.95)
        self.add_rule(r"(implementar|criar|função|classe|método|escrever.*código)", "coding", 0.90)
        self.add_rule(r"(revisar|review|PR|code review|qualidade|approve)", "review", 0.95)
        self.add_rule(r"(artigo|acadêmico|pesquisa|publicar|paper|dissertação|tese)", "academic", 0.90)
        self.add_rule(r"(apresentação|slides|palestra|talk|deck)", "presentation", 0.95)
        self.add_rule(r"(documentar|readme|API docs|documentação|docstring)", "documentation", 0.95)
        self.add_rule(r"(diagnosticar|saúde|health|audit|verificar|doctor|scanner)", "audit", 0.90)
        self.add_rule(r"(contrato|jurídico|petição|lei|advocacia|legal)", "legal", 0.95)

    def add_rule(self, pattern: str, label: str, confidence: float = 0.9):
        """Adiciona regra textual."""
        self._rules.append((pattern, label, confidence))

    def fit(
        self,
        texts: List[str],
        labels: List[str],
        max_features: int = 2000,
    ) -> "LocalClassifier":
        """
        Treina o classificador com exemplos.

        Args:
            texts: lista de textos de treino
            labels: lista de rótulos correspondentes
            max_features: máx features TF-IDF
        """
        unique_labels = sorted(set(labels))
        self._label_map = {l: i for i, l in enumerate(unique_labels)}
        self._reverse_map = {i: l for l, i in self._label_map.items()}

        y = np.array([self._label_map[l] for l in labels])

        self._pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                max_features=max_features,
                ngram_range=(1, 3),
                analyzer="word",
                lowercase=True,
                stop_words=["de", "da", "do", "em", "para", "com", "um", "uma",
                            "os", "as", "no", "na", "dos", "das", "por"],
            )),
            ("clf", LogisticRegression(
                C=1.0,
                max_iter=500,
                random_state=42,
            )),
        ])

        self._pipeline.fit(texts, y)
        self._is_fitted = True
        return self

    def predict(
        self,
        text: str,
        threshold: float = 0.15,
    ) -> Dict[str, Any]:
        """
        Classifica um texto.

        Args:
            text: texto a classificar
            threshold: confiança mínima para aceitar predição do modelo

        Returns:
            Dict com label, confidence, method, probas, elapsed_ms
        """
        start = time.time()
        self.stats["predictions"] += 1
        text_lower = text.lower()

        # 1. Regras textuais
        for pattern, label, confidence in self._rules:
            if re.search(pattern, text_lower):
                elapsed = (time.time() - start) * 1000
                self._update_avg(elapsed)
                self.stats["rule_matches"] += 1
                return {
                    "label": label,
                    "confidence": confidence,
                    "method": "rule",
                    "probas": {label: confidence},
                    "elapsed_ms": round(elapsed, 2),
                }

        # 2. Modelo
        if self._is_fitted and self._pipeline:
            try:
                probas = self._pipeline.predict_proba([text])[0]
                max_idx = int(np.argmax(probas))
                confidence = float(probas[max_idx])

                if confidence >= threshold:
                    label = self._reverse_map[max_idx]
                    all_probas = {
                        self._reverse_map[i]: float(p)
                        for i, p in enumerate(probas)
                    }

                    elapsed = (time.time() - start) * 1000
                    self._update_avg(elapsed)
                    self.stats["model_matches"] += 1
                    return {
                        "label": label,
                        "confidence": round(confidence, 4),
                        "method": "model",
                        "probas": all_probas,
                        "elapsed_ms": round(elapsed, 2),
                    }
            except Exception:
                pass

        # 3. Fallback
        elapsed = (time.time() - start) * 1000
        self._update_avg(elapsed)
        return {
            "label": "unknown",
            "confidence": 0.0,
            "method": "fallback",
            "probas": {},
            "elapsed_ms": round(elapsed, 2),
        }

    def predict_batch(
        self, texts: List[str], threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Classifica múltiplos textos."""
        return [self.predict(t, threshold) for t in texts]

    def save(self, name: str = "default") -> str:
        """Salva modelo em disco."""
        path = self.model_dir / f"{name}.pkl"
        data = {
            "pipeline": self._pipeline,
            "label_map": self._label_map,
            "reverse_map": self._reverse_map,
            "rules": self._rules,
        }
        with open(path, "wb") as f:
            pickle.dump(data, f)
        return str(path)

    def load(self, name: str = "default") -> bool:
        """Carrega modelo do disco."""
        path = self.model_dir / f"{name}.pkl"
        if not path.exists():
            return False
        with open(path, "rb") as f:
            data = pickle.load(f)
        self._pipeline = data["pipeline"]
        self._label_map = data["label_map"]
        self._reverse_map = data["reverse_map"]
        self._rules = data["rules"]
        self._is_fitted = self._pipeline is not None
        return True

    def _update_avg(self, elapsed_ms: float):
        n = self.stats["predictions"]
        self.stats["avg_ms"] = (
            (self.stats["avg_ms"] * (n - 1) + elapsed_ms) / n
        )

    def get_stats(self) -> Dict[str, Any]:
        return {
            **self.stats,
            "is_fitted": self._is_fitted,
            "rules_count": len(self._rules),
            "classes": len(self._label_map),
        }


def get_classifier(name: str = "default") -> LocalClassifier:
    """Retorna classificador carregado ou vazio."""
    clf = LocalClassifier()
    clf.load(name)
    return clf


# ─── Teste ───────────────────────────────────────────────────

if __name__ == "__main__":
    # Dados de treino: classificar intenção do usuário
    texts = [
        "preciso baixar um artigo do scihub", "quero fazer download de paper",
        "buscar biblioteca python", "encontrar pacote no pypi",
        "implementar função", "criar classe", "refatorar código",
        "revisar PR", "code review",
        "deploy em produção", "subir servidor",
        "escrever artigo acadêmico", "publicar pesquisa",
        "criar apresentação", "fazer slides",
        "documentar API", "escrever README",
        "diagnosticar ecossistema", "verificar saúde",
        "analisar contrato", "petição jurídica",
    ]
    labels = [
        "download_paper", "download_paper",
        "pypi_search", "pypi_search",
        "coding", "coding", "coding",
        "review", "review",
        "devops", "devops",
        "academic", "academic",
        "presentation", "presentation",
        "documentation", "documentation",
        "audit", "audit",
        "legal", "legal",
    ]

    clf = LocalClassifier()
    clf.add_rule(r"(sci.?hub|doi|paper|artigo|download.*pdf)", "download_paper", 0.95)
    clf.add_rule(r"(biblioteca|pacote|lib|pypi|pip)", "pypi_search", 0.95)
    clf.add_rule(r"(deploy|produção|produção|subir|servidor)", "devops", 0.95)
    clf.add_rule(r"(implementar|criar|função|classe|método)", "coding", 0.90)
    clf.add_rule(r"(revisar|review|PR|code review|qualidade)", "review", 0.95)
    clf.add_rule(r"(artigo|acadêmico|pesquisa|publicar|paper)", "academic", 0.90)
    clf.add_rule(r"(apresentação|slides|palestra)", "presentation", 0.95)
    clf.add_rule(r"(documentar|readme|API docs|documentação)", "documentation", 0.95)
    clf.add_rule(r"(diagnosticar|saúde|health|audit|verificar)", "audit", 0.90)
    clf.add_rule(r"(contrato|jurídico|petição|lei|advocacia)", "legal", 0.95)
    clf.fit(texts, labels)

    test_texts = [
        "preciso baixar um paper do scihub",
        "qual a melhor biblioteca para PDF?",
        "implementar função de validação",
        "fazer deploy em produção",
    ]

    print("=== LocalClassifier ===")
    print(f"Classes: {len(clf._label_map)} | Amostras treino: {len(texts)}\n")
    for t in test_texts:
        r = clf.predict(t)
        print(f'  "{t[:50]:50s}" → {r["label"]:20s} ({r["method"]}, conf={r["confidence"]})')

    print(f"\nStats: {clf.get_stats()}")
