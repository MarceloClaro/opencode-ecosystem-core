# SPEC-014-NAR: Narratologist Skill
Version: 1.0.0 | Status: draft | TDD: required

## Objective
Automated narrative structure analysis for fiction worldbuilding — identifying controlling idea, character arc integrity (want/need/lie), pacing peaks, and providing framework-cited structural recommendations.

## Acceptance Criteria
- [ ] CT-1: `structural_analysis()` identifies controlling idea and maps it to a recognized story structure paradigm (Three-Act, Hero's Journey, Save the Cat, Kishotenketsu, Freytag)
- [ ] CT-2: Character arc analysis extracts and validates the want/need/lie triad for every major character
- [ ] CT-3: Every recommendation cites its framework of origin (McKee, Campbell, Snyder, Vogler, Booker, Truby)
- [ ] CT-4: Pacing analysis identifies tension peaks and valleys with scene-level granularity; flags dead zones (3+ consecutive low-tension scenes)

## API Contract
- Class: NarratologistEngine
- Input:
  ```json
  {
    "story_title": "string",
    "synopsis": "string",
    "characters": [{"name": "string", "role": "protagonist | antagonist | mentor | ally | shadow"}],
    "structure_type": "three_act | hero_journey | save_the_cat | kishotenketsu | freytag | auto_detect",
    "analysis_depth": "structural_only | full_arc | comprehensive"
  }
  ```
- Output:
  ```json
  {
    "structural_analysis": {
      "controlling_idea": "string (value + cause)",
      "detected_structure": "string",
      "act_breakdown": [{"act": "string", "key_events": ["string"], "word_count_ratio": "float"}],
      "turning_points": [{"name": "string", "position_pct": "float", "impact": "HIGH | MEDIUM | LOW"}]
    },
    "character_arcs": [
      {
        "name": "string",
        "arc_type": "positive_change | negative_change | flat | tragic",
        "want": "string",
        "need": "string",
        "lie": "string",
        "moment_of_truth": "string",
        "arc_integrity_score": "0.0-1.0"
      }
    ],
    "pacing_analysis": {
      "tension_curve": [{"scene": "string", "tension": "0-10"}],
      "peaks": ["string"],
      "dead_zones": ["string"],
      "recommended_adjustments": ["string"]
    },
    "framework_recommendations": [
      {"framework": "string", "principle": "string", "application": "string", "urgency": "critical | important | optional"}
    ]
  }
  ```

## Constraints
- Controlling idea must follow McKee format: "Value X leads to Outcome Y because Cause Z"
- Want/need/lie triad is mandatory for protagonist; optional but recommended for other major characters
- Framework citation is non-negotiable — every recommendation must name its source
- Tension scoring 0-10 scale must be calibrated per genre conventions
- Dead zone detection threshold: 3+ consecutive scenes below genre tension baseline
