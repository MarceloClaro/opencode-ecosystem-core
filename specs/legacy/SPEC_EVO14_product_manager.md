# SPEC_EVO14_product_manager — Product Manager
## Domain: product | Agent: product-manager | Version: 1.0.0

### CT1: Opportunity assessment scoring
- **Given** reach=5000, impact=2.0, confidence=0.75, effort=6.0
- **When** `assess_opportunity` is called
- **Then** returns rice_score = 1250.0, recommendation must be one of ["BUILD","EXPLORE","DEFER","KILL"]
- **Assert** when rice_score >= 100, recommendation="BUILD"
- **Assert** when rice_score < 20, recommendation="KILL"

### CT2: Roadmap item validation
- **Given** item with name, owner, success_metric, time_horizon all set
- **When** `validate_roadmap_item` is called
- **Then** returns (True, "")
- **Given** item missing owner
- **When** `validate_roadmap_item` is called
- **Then** returns (False, error_message_containing "owner")

### CT3: Sprint health snapshot
- **Given** sprint with committed=[5,8,3], delivered=[5,3] (points)
- **When** `calculate_sprint_health` is called
- **Then** returns dict with velocity=16, completed=8, completion_pct=50.0
- **Assert** carried_over contains task with 3 points
- **Assert** blockers list non-empty when tasks not completed

### CT4: Scope change evaluation
- **Given** change request with source="Sales", priority="High"
- **When** `evaluate_scope_change` is called with sprint_goal="Improve onboarding"
- **Then** returns decision in ["ACCEPT","DEFER","REJECT"]
- **Assert** decision includes rationale string
- **Assert** impact_assessment contains timeline_impact field
