"""R666: planejamento evidenciado de capacidades, sem executar hipóteses."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from typing import Any


PLAN_KEYS = {"problem", "target_state", "modules", "candidates", "dependencies", "max_candidates"}
SCIENCE_KEYS = {"question", "dataset_csv", "dataset_provenance", "method", "variables", "output_dir", "reference_sources"}


def _finite_object(value: Any, allowed: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) - allowed:
        raise ValueError("Configuração deve ser objeto com campos reconhecidos.")
    try:
        payload = json.dumps(value, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValueError("Configuração deve conter JSON finito.") from exc
    if len(payload.encode("utf-8")) > 131072:
        raise ValueError("Configuração excede 128 KiB.")
    return json.loads(payload)


def _text(value: Any, name: str, limit: int = 2000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"{name} deve conter texto útil de até {limit} caracteres.")
    return value.strip()


def validate_plan_config(config: Any) -> dict[str, Any]:
    result = _finite_object(config, PLAN_KEYS)
    result["problem"] = _text(result.get("problem"), "problem")
    targets = result.get("target_state")
    if not isinstance(targets, list) or not 1 <= len(targets) <= 64:
        raise ValueError("target_state deve conter de 1 a 64 capacidades.")
    result["target_state"] = list(dict.fromkeys(_text(v, "capacidade", 240) for v in targets))
    limit = result.get("max_candidates", 32)
    if type(limit) is not int or not 1 <= limit <= 64:
        raise ValueError("max_candidates deve ser inteiro entre 1 e 64.")
    if "modules" in result and result["modules"] is not None:
        modules = result["modules"]
        if not isinstance(modules, dict) or len(modules) > 128:
            raise ValueError("modules deve ser mapa de até 128 módulos.")
        if any(not isinstance(v, list) for v in modules.values()) or sum(map(len, modules.values())) > 512:
            raise ValueError("modules deve conter listas de até 512 capacidades no total.")
        for key, records in modules.items():
            _text(key, "módulo", 240)
            for record in records:
                if isinstance(record, str):
                    _text(record, "capacidade", 240)
                elif isinstance(record, dict):
                    _text(record.get("id"), "capacidade", 240)
                    requires = record.get("requires", [])
                    if not isinstance(requires, list) or len(requires) > 64:
                        raise ValueError("requires deve ser lista limitada.")
                    for req in requires:
                        _text(req, "pré-requisito", 240)
                else:
                    raise ValueError("Capacidade deve ser ID ou descritor.")
    for key, maximum in (("candidates", 64), ("dependencies", 2048)):
        if key in result and result[key] is not None:
            if not isinstance(result[key], list) or len(result[key]) > maximum:
                raise ValueError(f"{key} deve ser lista limitada.")
            if any(not isinstance(v, dict) for v in result[key]):
                raise ValueError(f"Elementos de {key} devem ser objetos.")
    # Validação sem rede/escrita usa os mesmos contratos das camadas executadas.
    from scanners.capability_dna import normalize_modules
    from scanners.potentiality_scanner import PotentialityCandidate, PotentialityScanner
    from scanners.evolutionary_sequencing import EvolutionarySequencer
    modules = result.get("modules")
    if modules is not None:
        normalize_modules(modules)
    if result.get("candidates") is not None:
        try:
            candidates = [PotentialityCandidate(**record) for record in result["candidates"]]
            PotentialityScanner(modules=modules).scan(candidates, strict_ids=True)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Candidata inválida: {exc}") from exc
    if result.get("dependencies"):
        EvolutionarySequencer().plan(capabilities=[], dependencies=result["dependencies"],
                                    target_state=result["target_state"])
    return result


def validate_science_config(config: Any) -> dict[str, Any]:
    result = _finite_object(config, SCIENCE_KEYS)
    for key in ("question", "dataset_csv", "output_dir"):
        result[key] = _text(result.get(key), key)
    if result.get("method") not in {"pearson", "welch_t", "descriptive"}:
        raise ValueError("Método deve ser pearson, welch_t ou descriptive.")
    if not isinstance(result.get("dataset_provenance"), dict) or not isinstance(result.get("variables"), dict):
        raise ValueError("dataset_provenance e variables devem ser objetos.")
    from research.statistical_methods import validate_configuration
    validate_configuration(result["method"], result["variables"])
    if "reference_sources" in result and (not isinstance(result["reference_sources"], list)
                                          or not 1 <= len(result["reference_sources"]) <= 5):
        raise ValueError("reference_sources deve conter de 1 a 5 fontes.")
    return result


def _plain(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if is_dataclass(value):
        return asdict(value)
    return value


def scientific_modules() -> dict[str, list[dict[str, Any]]]:
    """Contrato estrutural do percurso. Declarações não são recibos de execução."""
    units = [
        ("primary_sources", [], [], ["references"], "Busca bibliográfica e verificação de DOI"),
        ("observational_dataset", [], [], ["dataset"], "Fonte pública, licença e hash dos dados"),
        ("method_execution", ["primary_sources", "observational_dataset"], ["dataset"], ["analysis"], "Cálculo delimitado e diagnóstico dos pressupostos"),
        ("reproduction", ["method_execution"], ["analysis"], ["reproduced_analysis"], "Reexecução e comparação numérica"),
        ("provenance_review", ["reproduction", "primary_sources"], ["reproduced_analysis"], ["reviewed_analysis"], "Revisão computacional e vinculação das afirmações"),
        ("academic_composition", ["provenance_review"], ["reviewed_analysis"], ["manuscript"], "Artefatos com resultados, referências e limitações"),
        ("reproducible_scientific_work", ["academic_composition"], ["manuscript"], ["research_package"], "Manifesto íntegro, sem alegar revisão por pares"),
    ]
    return {"scientific_provenance_pipeline": [
        {"id": key, "state": "declared", "requires": requires, "inputs": inputs,
         "outputs": outputs, "tags": ["science", "provenance"],
         "composition": {"conceitos": ["rastreabilidade", "incerteza"],
                         "metodos": [description], "bases": ["fontes primárias"],
                         "ferramentas": ["research.provenance_pipeline"],
                         "dominios": ["estatística", "engenharia de dados"],
                         "validacoes": [description], "recursos": ["dados e ambiente reproduzível"]},
         "validation_criteria": [description]}
        for key, requires, inputs, outputs, description in units]}


class KnowledgeEvolutionService:
    """Compõe as camadas existentes por contratos de capacidade, sem rede."""

    def plan(self, **config: Any) -> dict[str, Any]:
        config = validate_plan_config(config)
        from scanners.potentiality_scanner import PotentialityScanner, PotentialityCandidate, DEFAULT_MODULES
        from scanners.knowledge_composition import KnowledgeComposition
        from scanners.evolutionary_sequencing import EvolutionarySequencer
        from scanners.polymathic_convergence import PolymathicConvergence

        modules = config.get("modules")
        if modules is None:
            modules = {**DEFAULT_MODULES, **scientific_modules()}
        scanner = PotentialityScanner(modules=modules)
        dna = scanner.extract_dna()
        maximum = config.get("max_candidates", 32)
        if config.get("candidates") is not None:
            candidates = [PotentialityCandidate(**value) for value in config["candidates"]]
            potentials = scanner.scan(candidates)
        else:
            candidates = scanner.discover(max_candidates=maximum, max_pair_checks=256)
            potentials = scanner.scan(candidates)
        potential_report = _plain(potentials)
        # Candidatas podem ser planejadas, mas nunca entram como execução observada.
        hypotheses = [{"id": candidate.id, "state": "declared", "requires": candidate.requires,
                       "evidence": [{"kind": "hypothesis", "ref": f"candidate:{candidate.id}",
                                     "success": True}]} for candidate in candidates
                      if candidate.id not in dna["capability_map"]]
        if hypotheses:
            provider = "emergence_hypotheses"
            while provider in modules:
                provider = "_" + provider
            dna = PotentialityScanner(modules={**modules, provider: hypotheses}).extract_dna()
        cap_map = dna["capability_map"]
        observed = sorted(key for key, value in cap_map.items()
                          if value["state"] in {"executed", "externally_validated"})
        edges = []
        for index, raw in enumerate(list(dna.get("dependencies", [])) + list(config.get("dependencies") or [])):
            edge = dict(raw)
            edge.setdefault("necessity", "hypothesis")
            if not edge.get("evidence"):
                edge["evidence"] = [{"kind": "structural_declaration",
                                     "ref": edge.get("origin", f"request:dependencies:{index}"),
                                     "success": True}]
            edges.append(edge)
        targets = config["target_state"]
        capabilities = []
        for key, value in cap_map.items():
            record = dict(value, id=key)
            if not record.get("evidence"):
                record["evidence"] = [{"kind": "structural_declaration", "ref": origin,
                                       "success": True} for origin in value.get("origins", [])]
            capabilities.append(record)
        sequence = EvolutionarySequencer().plan(capabilities=capabilities, dependencies=edges,
                                               target_state=targets, observed=observed)
        # A composição preserva também as capacidades ausentes que o plano cita.
        needed = set(targets)
        for _ in range(64):
            previous = set(needed)
            for edge in edges:
                if edge.get("relation") == "requires" and edge.get("source") in needed:
                    needed.add(edge["target"])
                elif edge.get("relation") == "enables" and edge.get("target") in needed:
                    needed.add(edge["source"])
            if needed == previous:
                break
        composer = KnowledgeComposition()
        composition = _plain(composer.compose_many(sorted(needed), dna=dna, candidates=candidates))
        potential_successors = []
        for candidate in candidates[:maximum]:
            successor = EvolutionarySequencer().plan(capabilities=capabilities, dependencies=edges,
                                                     target_state=[candidate.id], observed=observed)
            potential_successors.append({"id": candidate.id, "description": candidate.description,
                                         "origin": candidate.origin, "hypothesis": True,
                                         "executed": False, "requires": candidate.requires,
                                         "composition": _plain(composer.compose(candidate.id, dna=dna,
                                                                                candidate=candidate)),
                                         "sequencing": successor})
        convergence = PolymathicConvergence()
        analogies = {cap: [_plain(match) for match in convergence.match_capability(cap)]
                     for cap in sorted(needed - set(observed))}
        blocked = bool(sequence.get("status") == "blocked" or sequence.get("missing_dependencies")
                       or sequence.get("blocked_nodes"))
        result = {"status": "blocked" if blocked else "planned", "problem": config["problem"],
                  "target_state": targets, "executed": False, "externally_validated": False,
                  "score_kind": "heuristic", "dna": dna, "observed_capabilities": observed,
                  "evolution_gap": sequence["evolution_gap"], "structural_closure": sorted(needed),
                  "potentiality": potential_report,
                  "composition": composition, "sequencing": sequence,
                  "potential_successors": potential_successors,
                  "polymathic_convergence": {"matches": analogies, "origin": "curated_lexical_matching",
                                             "warnings": convergence.warnings},
                  "limits": ["Potenciais e analogias são hipóteses estruturais.",
                             "Cronograma e resistência são estimativas, sem probabilidade calibrada.",
                             "Evidências recebidas precisam ser auditadas no seu contexto.",
                             "O plano não executa, instala ou valida externamente capacidades."]}
        payload = json.dumps(result, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()
        result["report_sha256"] = hashlib.sha256(payload).hexdigest()
        return result
