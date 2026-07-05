# SPEC_EVO14_product_nudge — Behavioral Nudge Engine
## Domain: product | Agent: behavioral-nudge | Version: 1.0.0

### CT1: ADHD/overwhelmed profile micro-sprint
- **Given** user with tendencies=["ADHD"] and 50 pending tasks
- **When** `generate_sprint_nudge` is called
- **Then** returns dict with channel="SMS", message containing "5 mins"
- **Assert** message does NOT mention the number 50

### CT2: Standard profile task summary
- **Given** user with tendencies=[] and 5 pending tasks
- **When** `generate_sprint_nudge` is called
- **Then** returns dict with channel="EMAIL"
- **Assert** message contains the number 5 and highest priority task title

### CT3: Nudge sequence logic
- **Given** day=1, user with preferred_channel="SMS"
- **When** `get_nudge_channel` is called
- **Then** returns "SMS"
- **Given** day=5, user with preferred_channel="in_app"
- **When** `get_nudge_channel` is called with fallback_sequence
- **Then** returns "EMAIL" (Day 5 falls into email bracket)

### CT4: Celebration message generation
- **Given** completed_tasks=15, total_minutes=12
- **When** `generate_celebration` is called
- **Then** returns string containing congratulatory tone
- **Assert** message offers continuation choice ("Want to do another 5 minutes?")
- **Assert** message includes off-ramp option
