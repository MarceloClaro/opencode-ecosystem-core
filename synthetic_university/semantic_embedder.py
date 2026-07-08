"""Semantic Embedder for ConceptEmbeddingSpace — SPEC-935 R75.

Substitui o embedding lexical (Jaccard) por embedding semântico neural
usando o modelo nomic-embed-text via Ollama.

Arquitetura:
  1. Ollama Embedder (nomic-embed-text, 768-dim) via API local
  2. Cache LRU para evitar re-embedding
  3. Fallback LSA (TF-IDF + Gram matrix) quando Ollama ausente
  4. Interface compatível com ConceptEmbeddingSpace → drop-in replacement

Referência: nomic-embed-text é um modelo de embedding contrastivo
treinado com dados multilíngues, state-of-the-art para similaridade semântica.
"""

from __future__ import annotations
import json
import math
import logging
import time
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Set, Tuple
from itertools import combinations
from collections import OrderedDict, Counter

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
OLLAMA_URL = "http://localhost:11434/api/embeddings"
OLLAMA_MODEL = "nomic-embed-text"
EMBED_DIM = 768          # nomic-embed-text output dimension
CACHE_SIZE = 8192        # LRU cache capacity
LSA_FALLBACK_DIM = 64
SIMILARITY_EPSILON = 1e-8

STOPWORDS: Set[str] = {
    "que", "para", "com", "dos", "das", "uma", "mais",
    "como", "por", "mas", "seu", "sua", "pelo", "pela",
    "entre", "onde", "sobre", "após", "até", "sem",
    "são", "era", "foi", "seus", "suas", "qual",
    "quais", "quem", "cada", "todo", "toda", "todos", "todas",
    "aos", "nas", "nos", "num", "numa",
    "isto", "isso", "aquilo", "este", "esta", "esse", "essa",
    "aquele", "aquela", "mesmo", "outro", "outra",
    "muito", "pouco", "tanto", "quanto",
    "algum", "alguma", "nenhum", "nenhuma", "qualquer",
    "através", "durante", "mediante", "excepto", "menos",
    "conforme", "consoante", "segundo", "salvo",
}


# ---------------------------------------------------------------------------
# Ollama Neural Embedder
# ---------------------------------------------------------------------------

class SemanticEmbedder:
    """Embedder semântico neural via Ollama (nomic-embed-text).
    
    Características:
    - Embeddings de 768 dimensões com contexto semântico real
    - Cache LRU para reuso
    - Fallback LSA quando Ollama não responde
    - Batch embedding eficiente para corpus
    """

    def __init__(self, dimension: int = EMBED_DIM):
        self.dimension = dimension
        self._ollama_available: Optional[bool] = None
        self._embed_cache: OrderedDict = OrderedDict()
        self._cache_size = CACHE_SIZE
        
        # Fallback LSA
        self._lsa_embedder: Optional['_LSAFallback'] = None
        self._doc_texts: List[str] = []
        self._doc_text_index: Dict[str, int] = {}  # O(1) lookup
        self._doc_embeddings: List[np.ndarray] = []  # cache do corpus
        self._fitted = False

    # ------------------------------------------------------------------
    # Corpus building
    # ------------------------------------------------------------------

    def build_corpus(self, texts: List[str]):
        """Constrói o corpus: embed todos os textos e prepara fallback LSA."""
        logger.info(f"SemanticEmbedder: processando {len(texts)} textos")

        if not texts:
            self._fitted = True
            return

        # Tentar embed em batch via Ollama
        self._doc_texts = texts
        self._doc_text_index = {t: i for i, t in enumerate(texts)}
        self._doc_embeddings = []
        success_count = 0

        # Embed em lote (agrupado para eficiência)
        batch_size = 64
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = []
            for text in batch:
                vec = self._ollama_embed_single(text)
                if vec is not None:
                    batch_embeddings.append(vec)
                    success_count += 1
                else:
                    break  # Ollama falhou → usar fallback LSA
            if len(batch_embeddings) == len(batch):
                self._doc_embeddings.extend(batch_embeddings)
            else:
                self._doc_embeddings = []
                break

        # Se Ollama funcionou para todos
        if len(self._doc_embeddings) == len(texts):
            self._ollama_available = True
            logger.info(f"  ✅ Ollama embeddings: {success_count}/{len(texts)} sucesso")
            self._fitted = True
            return

        # Fallback: LSA
        logger.info(f"  ⚠️ Ollama indisponível ou incompleto. Usando fallback LSA...")
        self._fallback_to_lsa(texts)
        self._fitted = True

    def _ollama_embed_single(self, text: str) -> Optional[np.ndarray]:
        """Embedding de um texto via Ollama. Retorna None se falhar."""
        # Verificar cache
        if text in self._embed_cache:
            self._embed_cache.move_to_end(text)
            return self._embed_cache[text]

        if self._ollama_available is False:
            return None

        try:
            data = json.dumps({
                "model": OLLAMA_MODEL,
                "prompt": text,
            }).encode()
            req = urllib.request.Request(
                OLLAMA_URL,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                vec = np.array(result.get("embedding", []), dtype=np.float32)
                if len(vec) == 0:
                    return None
                # Normalização L2
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec / norm
                # Cache LRU
                if len(self._embed_cache) >= self._cache_size:
                    self._embed_cache.popitem(last=False)
                self._embed_cache[text] = vec
                return vec
        except (urllib.error.URLError, urllib.error.HTTPError,
                json.JSONDecodeError, ConnectionError, TimeoutError,
                OSError) as e:
            logger.warning(f"  Ollama error: {e}")
            self._ollama_available = False
            return None

    def _fallback_to_lsa(self, texts: List[str]):
        """Fallback: LSA via Gram matrix."""
        try:
            self._lsa_embedder = _LSAFallback(dimension=LSA_FALLBACK_DIM)
            self._lsa_embedder.build_corpus(texts)
            self._doc_embeddings = self._lsa_embedder.doc_embeddings
            self._ollama_available = False
            logger.info(f"  Fallback LSA: {len(self._doc_embeddings)} embeddings")
        except Exception as e:
            logger.error(f"  Fallback LSA falhou: {e}")
            self._doc_embeddings = []

    # ------------------------------------------------------------------
    # Embedding (ponto de entrada único)
    # ------------------------------------------------------------------

    def embed(self, text: str) -> np.ndarray:
        """Embedding de um texto. Prioriza cache do corpus, depois Ollama."""
        # 1. Cache do corpus (mais rápido — lookup O(1) com dict)
        if text in self._doc_text_index:
            idx = self._doc_text_index[text]
            if idx < len(self._doc_embeddings):
                return self._doc_embeddings[idx]
        
        # 2. Cache LRU (Ollama já chamado antes)
        if text in self._embed_cache:
            self._embed_cache.move_to_end(text)
            return self._embed_cache[text]
        
        # 3. Ollama API
        vec = self._ollama_embed_single(text)
        if vec is not None:
            return vec

        # 4. Fallback final
        logger.warning(f"  Embedding não disponível para: '{text[:50]}...'")
        return np.zeros(self.dimension, dtype=np.float32)

    # ------------------------------------------------------------------
    # Persistência (salvar/carregar embeddings para reuso)
    # ------------------------------------------------------------------

    def save(self, path: str):
        """Salva embeddings do corpus em disco para reuso rápido."""
        import pickle
        data = {
            'doc_texts': self._doc_texts,
            'doc_embeddings': self._doc_embeddings,
            'ollama_available': self._ollama_available,
            'dimension': self.dimension,
        }
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        logger.info(f"Embeddings salvos: {path} ({len(self._doc_embeddings)} vetores)")

    def load(self, path: str) -> bool:
        """Carrega embeddings do disco. Retorna True se sucesso."""
        import pickle
        import os
        if not os.path.exists(path):
            return False
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
            self._doc_texts = data['doc_texts']
            self._doc_text_index = {t: i for i, t in enumerate(self._doc_texts)}
            self._doc_embeddings = data['doc_embeddings']
            self._ollama_available = data.get('ollama_available', True)
            self.dimension = data.get('dimension', EMBED_DIM)
            self._fitted = True
            logger.info(f"Embeddings carregados: {path} ({len(self._doc_embeddings)} vetores)")
            return True
        except Exception as e:
            logger.warning(f"Falha ao carregar embeddings: {e}")
            return False

    # ------------------------------------------------------------------
    # Similarity / Coherence / Diversity
    # ------------------------------------------------------------------

    def similarity(self, text_a: str, text_b: str) -> float:
        """Cosine similarity entre dois textos."""
        if text_a == text_b:
            return 1.0

        vec_a = self.embed(text_a)
        vec_b = self.embed(text_b)

        if np.linalg.norm(vec_a) < SIMILARITY_EPSILON or \
           np.linalg.norm(vec_b) < SIMILARITY_EPSILON:
            return 0.0

        dot = float(np.dot(vec_a, vec_b))
        # Já normalizados L2, dot = cosine
        return max(0.0, min(1.0, dot))

    def coherence(self, texts: List[str]) -> float:
        """Coerência média entre todos os pares."""
        if len(texts) <= 1:
            return 1.0
        scores = [self.similarity(a, b) for a, b in combinations(texts, 2)]
        return sum(scores) / len(scores) if scores else 0.5

    def diversity(self, texts: List[str]) -> float:
        return 1.0 - self.coherence(texts)


# ---------------------------------------------------------------------------
# LSA Fallback (TF-IDF + Gram matrix spectral decomposition)
# ---------------------------------------------------------------------------

class _LSAFallback:
    """Fallback LSA eficiente para quando Ollama não está disponível."""

    def __init__(self, dimension: int = 64):
        self.dimension = dimension
        self.doc_embeddings: List[np.ndarray] = []

    def build_corpus(self, texts: List[str]):
        """Constrói LSA a partir do corpus."""
        # Tokenização
        tokenized: List[List[str]] = [self._tokenize(t) for t in texts]
        tokenized = [t for t in tokenized if t]

        if len(tokenized) < 2:
            self.doc_embeddings = [np.ones(1, dtype=np.float32) for _ in texts]
            return

        # Term frequency
        from collections import Counter
        term_doc_freq: Dict[str, int] = {}
        for tokens in tokenized:
            for t in set(tokens):
                term_doc_freq[t] = term_doc_freq.get(t, 0) + 1

        # Filter vocabulary
        n_docs = len(tokenized)
        max_df = max(1, int(n_docs * 0.75))
        vocab: Dict[str, int] = {}
        for t, df in sorted(term_doc_freq.items(), key=lambda x: -x[1]):
            if df >= 2 and df <= max_df:
                vocab[t] = len(vocab)

        if len(vocab) < 3:
            self.doc_embeddings = [np.ones(1, dtype=np.float32) for _ in texts]
            return

        # TF-IDF sparse
        tfidf: List[Dict[int, float]] = []
        for tokens in tokenized:
            counter = Counter(tokens)
            max_tf = max(counter.values()) or 1
            vec = {}
            for term, count in counter.items():
                if term in vocab:
                    tf = count / max_tf
                    idf = math.log((n_docs + 1) / (term_doc_freq[term] + 1)) + 1.0
                    vec[vocab[term]] = tf * idf
            norm = math.sqrt(sum(w * w for w in vec.values()))
            if norm > 0:
                vec = {k: v / norm for k, v in vec.items()}
            tfidf.append(vec)

        # Gram matrix
        gram = np.eye(n_docs, dtype=np.float32)
        for i in range(n_docs):
            vi = tfidf[i]
            if not vi:
                continue
            for j in range(i + 1, n_docs):
                vj = tfidf[j]
                if not vj:
                    continue
                smaller, larger = (vi, vj) if len(vi) <= len(vj) else (vj, vi)
                dot = 0.0
                for idx, w in smaller.items():
                    w2 = larger.get(idx)
                    if w2 is not None:
                        dot += w * w2
                gram[i, j] = dot
                gram[j, i] = dot

        # Spectral decomposition
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(gram)
        except np.linalg.LinAlgError:
            self.doc_embeddings = [np.ones(1, dtype=np.float32) for _ in texts]
            return

        k = min(self.dimension, n_docs - 1)
        idx_desc = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx_desc]
        eigenvectors = eigenvectors[:, idx_desc]

        positive = eigenvalues > 1e-10
        k = min(k, int(positive.sum()))
        if k < 2:
            k = 2

        sqrt_eig = np.sqrt(np.maximum(eigenvalues[:k], 1e-10))
        embeddings = eigenvectors[:, :k] * sqrt_eig
        norms = np.maximum(np.linalg.norm(embeddings, axis=1, keepdims=True), 1e-8)
        embeddings = embeddings / norms

        self.doc_embeddings = [embeddings[i].copy() for i in range(n_docs)]

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        tokens = []
        for word in text.lower().split():
            word = word.strip(".,;:!?()[]{}""''«»-–—")
            if len(word) >= 3 and word not in STOPWORDS:
                tokens.append(word)
        return tokens


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_semantic_embedder(texts: Optional[List[str]] = None,
                              cache_path: str = "/tmp/semantic_embedder.pkl") -> SemanticEmbedder:
    """Cria SemanticEmbedder, tentando cache primeiro.
    
    Args:
        texts: Textos do corpus (se None, tenta carregar do cache)
        cache_path: Caminho do cache persistente
    """
    embedder = SemanticEmbedder(dimension=EMBED_DIM)
    
    # Tentar carregar do cache
    if texts is None or embedder.load(cache_path):
        if embedder._fitted:
            logger.info(f"Embedder carregado de cache: {cache_path}")
            return embedder
    
    # Construir corpus e salvar cache
    if texts:
        embedder.build_corpus(texts)
        embedder.save(cache_path)
    
    return embedder
