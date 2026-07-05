# SPEC-014-HIS: Historian Skill
Version: 1.0.0 | Status: draft | TDD: required

## Objective
Automated historical authenticity validation for worldbuilding — detecting anachronisms, enriching material culture, correcting popular myths, and producing period-authentic reports with calibrated confidence.

## Acceptance Criteria
- [ ] CT-1: `detect_anachronisms()` achieves 85%+ accuracy on validated test corpus of 100+ known anachronistic pairs
- [ ] CT-2: Period authenticity report contains all required sections (technology, social structure, material culture, trade, belief systems)
- [ ] CT-3: Confidence levels explicitly stated for every claim (HIGH: primary sources / MEDIUM: scholarly consensus / LOW: extrapolation)
- [ ] CT-4: Non-Western historical traditions included in at least 30% of reference pool (Chinese, Islamic, Indian, Mesoamerican, African)

## API Contract
- Class: HistorianEngine
- Input:
  ```json
  {
    "period": "string (e.g., 'Late Bronze Age Aegean')",
    "region": "string",
    "tech_level": "paleolithic | neolithic | bronze_age | iron_age | classical | medieval | early_modern | industrial",
    "query_type": "authenticity_report | anachronism_check | material_enrichment | myth_correction"
  }
  ```
- Output:
  ```json
  {
    "period_authenticity_report": {
      "technology": {"available": ["string"], "absent": ["string"], "confidence": "HIGH | MEDIUM | LOW"},
      "social_structure": {"classes": ["string"], "mobility": "string", "confidence": "HIGH | MEDIUM | LOW"},
      "material_culture": {"diet": ["string"], "clothing": ["string"], "architecture": ["string"]},
      "trade_networks": {"imports": ["string"], "exports": ["string"], "partners": ["string"]},
      "belief_systems": {"dominant": "string", "practices": ["string"]}
    },
    "anachronisms": [
      {
        "element": "string",
        "period_claimed": "string",
        "actual_origin": "string",
        "offset_years": "integer",
        "source": "string"
      }
    ],
    "myth_corrections": [
      {"myth": "string", "reality": "string", "origin_of_myth": "string", "scholarly_consensus": "HIGH | MEDIUM | LOW"}
    ],
    "non_western_parallels": [
      {"civilization": "string", "contemporary_development": "string", "relevance": "string"}
    ]
  }
  ```

## Constraints
- Every claim must be traceable to a historical period with evidence grade
- Anachronism detection must cross-reference technology, social norms, language, and material culture
- Myth correction must cite origin of the myth (e.g., 19th c. romanticism, Hollywood, Victorian historiography)
- Non-Western inclusion is mandatory, not optional — min 30% reference diversity
- Confidence LOW must trigger a warning; no LOW-confidence claim may appear without explicit flag
