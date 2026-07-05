# SPEC_EVO14_product_trend — Trend Researcher
## Domain: product | Agent: trend-researcher | Version: 1.0.0

### CT1: Trend lifecycle classification
- **Given** trend with growth_rate=0.5, mention_volume=100, age_months=3
- **When** `classify_lifecycle` is called
- **Then** returns "EMERGENCE"
- **Given** trend with growth_rate=0.05, mention_volume=5000, age_months=24
- **When** `classify_lifecycle` is called
- **Then** returns "MATURITY"

### CT2: Market sizing (TAM/SAM/SOM)
- **Given** total_population=1000000, target_pct=0.15, reachable_pct=0.4, competitive_share=0.1
- **When** `calculate_market_size` is called
- **Then** TAM=150000, SAM=60000, SOM=6000
- **Assert** TAM >= SAM >= SOM

### CT3: Signal strength scoring
- **Given** signals with varied sources and weights
- **When** `calculate_signal_strength` is called
- **Then** returns score in range [0, 100]
- **Assert** social_media signals contribute 0.3 weight
- **Assert** patent signals contribute 0.2 weight
- **Assert** investment signals contribute 0.25 weight

### CT4: Competitive positioning matrix
- **Given** competitors list with feature vectors
- **When** `build_positioning_matrix` is called
- **Then** returns matrix with rows=competitors, columns=features
- **Assert** includes "differentiation_score" per competitor
- **Assert** identifies "white_space" features (not covered by any competitor)
