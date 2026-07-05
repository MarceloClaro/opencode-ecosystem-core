# SPEC-014-GEO: Geographer Skill
Version: 1.0.0 | Status: draft | TDD: required

## Objective
Automated geographic worldbuilding validation ensuring physical geography obeys natural laws — climate consistency, hydrological correctness, and settlement logic grounded in terrain and resources.

## Acceptance Criteria
- [ ] CT-1: `validate_geography()` checks climate/terrain consistency against latitude, altitude, and wind patterns
- [ ] CT-2: Rivers obey hydrology rules (flow downhill, merge don't split, drain to ocean/basin)
- [ ] CT-3: Settlement patterns have geographic justification (water access, arable land, defensible terrain, trade routes)
- [ ] CT-4: Climate system design follows Koppen classification with correct latitude-temperature-precipitation relationships

## API Contract
- Class: GeographerEngine
- Input:
  ```json
  {
    "region_name": "string",
    "coordinates": {"lat": "float", "lon": "float"},
    "terrain_types": ["mountain", "plain", "coastal", "desert"],
    "scale": "continental | regional | local",
    "existing_map": "string (optional)"
  }
  ```
- Output:
  ```json
  {
    "climate_zone": {
      "koppen_classification": "Af | Am | Aw | BWh | BWk | BSh | BSk | Csa | Csb | Cfa | Cfb | Cfc | Dfa | Dfb | Dfc | Dfd | ET | EF",
      "temperature_range": {"min": "float", "max": "float"},
      "precipitation_pattern": "string",
      "biome": "string"
    },
    "hydrology_validation": {
      "rivers": [{"name": "string", "source": "coords", "mouth": "coords", "violations": ["string"]}],
      "watersheds": ["string"],
      "score": "0.0-1.0"
    },
    "settlement_analysis": {
      "locations": [{"name": "string", "rationale": "string", "viability_score": "0.0-1.0"}],
      "trade_routes": [{"from": "string", "to": "string", "terrain_challenges": ["string"]}]
    },
    "geographic_coherence_report": {
      "overall_score": "0.0-1.0",
      "violations": [{"type": "string", "severity": "critical | major | minor", "fix": "string"}],
      "recommendations": ["string"]
    }
  }
  ```

## Constraints
- Climate must be derived from lat+alt+wind, never claimed arbitrarily
- Rivers must obey dendritic pattern rules (no bifurcation except deltas)
- Every settlement must cite at least 2 geographic justification factors
- Koppen classification must use updated 2018 Chen & Chen criteria
- Coherence report is mandatory — no silent acceptance of geographic impossibilities
