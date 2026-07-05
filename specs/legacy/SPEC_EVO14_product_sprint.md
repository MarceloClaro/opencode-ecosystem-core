# SPEC_EVO14_product_sprint — Sprint Prioritizer
## Domain: product | Agent: sprint-prioritizer | Version: 1.0.0

### CT1: RICE score calculation
- **Given** Reach=2000, Impact=3, Confidence=0.9, Effort=5
- **When** `calculate_rice` is called
- **Then** returns (2000*3*0.9)/5 = 1080.0
- **Given** negative Reach
- **When** `calculate_rice` is called
- **Then** raises ValueError

### CT2: MoSCoW classification
- **Given** items with rice_scores [500, 150, 30, 8, 300, 80]
- **When** `classify_moscow` is called
- **Then** top 20% are "Must Have", next 30% "Should Have", next 30% "Could Have", bottom 20% "Won't Have"
- **Assert** each item has exactly one classification

### CT3: Sprint capacity planning
- **Given** velocity=30, team_size=5, buffer_pct=15
- **When** `plan_sprint_capacity` is called
- **Then** returns effective_capacity = 30 * (1 - 0.15) = 25.5
- **Assert** recommended_commitment does not exceed effective_capacity

### CT4: Dependency resolution
- **Given** tasks with cross-dependencies
- **When** `resolve_dependencies` is called
- **Then** returns topologically sorted task list
- **Assert** no task appears before its dependencies
- **Given** circular dependency
- **When** `resolve_dependencies` is called
- **Then** raises ValueError with cycle information
