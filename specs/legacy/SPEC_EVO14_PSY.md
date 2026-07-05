# SPEC-014-PSY: Psychologist Skill
Version: 1.0.0 | Status: draft | TDD: required

## Objective
Automated psychological profiling for fictional characters using Big Five + attachment theory, defense mechanism identification (Vaillant hierarchy), and interpersonal dynamics analysis — explicitly avoiding diagnostic reductionism.

## Acceptance Criteria
- [ ] CT-1: `psychological_profile()` uses Big Five (OCEAN) dimensions + attachment style (secure / anxious / avoidant / disorganized) for each character
- [ ] CT-2: Defense mechanisms identified and classified per Vaillant's hierarchy (Level I psychotic → Level IV mature)
- [ ] CT-3: Output contains an explicit "This is not a clinical diagnosis" disclaimer; no DSM/ICD codes or clinical labels applied to fictional characters
- [ ] CT-4: Interpersonal dynamics analyzed via dyadic compatibility (attachment pairing, OCEAN complementarity/gap analysis)

## API Contract
- Class: PsychologistEngine
- Input:
  ```json
  {
    "characters": [
      {
        "name": "string",
        "backstory": "string",
        "behaviors": ["string"],
        "relationships": [{"with": "string", "type": "familial | romantic | rivalry | mentorship | friendship"}]
      }
    ],
    "analysis_type": "profile | dynamics | defense_mechanisms | comprehensive"
  }
  ```
- Output:
  ```json
  {
    "disclaimer": "This is a fictional character analysis for creative worldbuilding. It is not a clinical diagnosis.",
    "profiles": [
      {
        "name": "string",
        "big_five": {
          "openness": {"score": "0-100", "facets": ["string"]},
          "conscientiousness": {"score": "0-100", "facets": ["string"]},
          "extraversion": {"score": "0-100", "facets": ["string"]},
          "agreeableness": {"score": "0-100", "facets": ["string"]},
          "neuroticism": {"score": "0-100", "facets": ["string"]}
        },
        "attachment_style": "secure | anxious | avoidant | disorganized",
        "defense_mechanisms": [
          {"name": "string", "level": "I | II | III | IV", "trigger_context": "string", "adaptive_value": "maladaptive | immature | neurotic | mature"}
        ],
        "core_conflict": "string",
        "behavioral_consistency_score": "0.0-1.0"
      }
    ],
    "interpersonal_dynamics": [
      {
        "pair": ["char_a", "char_b"],
        "attachment_compatibility": "high | moderate | low | conflict_prone",
        "ocean_gaps": {"dimension": "string", "gap_size": "float", "projected_friction": "string"},
        "dynamic_pattern": "complementary | mirroring | oppositional | enmeshed | distant",
        "growth_potential": "HIGH | MEDIUM | LOW"
      }
    ]
  }
  ```

## Constraints
- Mandatory disclaimer at output root — no exceptions
- Defense mechanism classification must use Vaillant (1992) four-level hierarchy
- Attachment style must follow Bartholomew & Horowitz (1991) four-category model
- OCEAN facets must reference at least 2 facets per dimension (NEO-PI-R subset)
- DSM/ICD codes, clinical diagnoses, and medicalizing language are banned from output
- Behavioral consistency score < 0.5 must flag character as incoherently written
