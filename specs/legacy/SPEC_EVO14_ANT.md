# SPEC-014-ANT: Anthropologist Skill
Version: 1.0.0 | Status: draft | TDD: required

## Objective
Enable automated cultural system analysis for worldbuilding via functional-structural anthropology, kinship validation, and ritual function assessment.

## Acceptance Criteria
- [ ] CT-1: `analyze_culture()` returns structured functional analysis with components (economy, kinship, religion, politics, symbols) and their interrelations
- [ ] CT-2: `coherence_check()` identifies internal contradictions in cultural systems with severity classification (fatal / major / minor)
- [ ] CT-3: Kinship rules validated against established anthropological typologies (Iroquois, Omaha, Crow, Eskimo, Sudanese, Hawaiian)
- [ ] CT-4: Output contains zero cultural cliches (noble savage, mystical native, monolithic tradition) — verified via banned-pattern filter

## API Contract
- Class: AnthropologistEngine
- Input:
  ```json
  {
    "culture_name": "string",
    "components": ["economy", "kinship", "religion", "politics"],
    "depth": "basic | standard | comprehensive",
    "existing_context": "string (optional)"
  }
  ```
- Output:
  ```json
  {
    "functional_analysis": {
      "component": "string",
      "function": "string",
      "interdependencies": ["string"],
      "coherence_score": "0.0-1.0"
    },
    "kinship_system": {
      "typology": "Iroquois | Omaha | Crow | Eskimo | Sudanese | Hawaiian",
      "descent": "patrilineal | matrilineal | bilateral",
      "residence": "patrilocal | matrilocal | neolocal | avunculocal",
      "terminology": {}
    },
    "contradictions": [
      {
        "elements": ["element_a", "element_b"],
        "type": "logical | practical | symbolic",
        "severity": "fatal | major | minor",
        "resolution_suggestion": "string"
      }
    ],
    "ritual_analysis": {
      "rite_type": "calendrical | crisis | passage | intensification",
      "social_function": "string",
      "symbolic_elements": ["string"]
    }
  }
  ```

## Constraints
- Must cite at least one canonical anthropological framework (Malinowski, Radcliffe-Brown, Levi-Strauss, Geertz, Douglas)
- Kinship classification must map to Murdock's six-type typology
- Banned cultural cliche patterns enforced at output validation layer
- Functional analysis requires minimum 4 cultural components present
- Coherence check must run pairwise across all components (O(n²) completeness)
