# SPEC_EVO14_product_feedback — Feedback Synthesizer
## Domain: product | Agent: feedback-synthesizer | Version: 1.0.0

### CT1: Sentiment scoring
- **Given** feedback text "This feature is amazing, love it!"
- **When** `analyze_sentiment` is called
- **Then** returns score > 0.5 (positive), confidence >= 0.7
- **Given** feedback text "This is terrible, worst update ever"
- **When** `analyze_sentiment` is called
- **Then** returns score < -0.5 (negative), confidence >= 0.7

### CT2: Theme categorization
- **Given** feedback items with varied content
- **When** `categorize_feedback` is called
- **Then** returns dict mapping themes to feedback counts
- **Assert** theme "performance" detects phrases like "slow", "lag", "loading"
- **Assert** theme "ux" detects phrases like "confusing", "hard to find", "navigation"

### CT3: Priority scoring (RICE)
- **Given** feature request with reach=1000, impact=2, confidence=0.8, effort=4
- **When** `calculate_rice_score` is called
- **Then** returns score = (1000*2*0.8)/4 = 400.0
- **Given** edge case with effort=0
- **When** `calculate_rice_score` is called
- **Then** raises ValueError

### CT4: Feedback summary generation
- **Given** 20 feedback items with mixed sentiment
- **When** `generate_summary` is called
- **Then** returns dict with total_count, sentiment_distribution, top_themes (max 5)
- **Assert** sentiment_distribution sums to total_count
- **Assert** top_themes sorted by frequency descending
