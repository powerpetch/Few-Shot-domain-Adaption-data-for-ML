# Caption Validation Checklist

## Purpose
This checklist ensures all generated captions meet quality standards and accurately describe the crystallization phases.

---

## Quality Criteria

### 1. Phase Identification ✓
- [ ] Caption clearly identifies the phase (Unsaturated/Labile/Intermediate/Metastable)
- [ ] Phase name matches the image label
- [ ] No confusion between phases

**Example:** "LABILE: Very small crystal nuclei..."

### 2. Visual Description ✓
- [ ] Describes what's visible in the image
- [ ] Mentions crystal particles/seeds if present
- [ ] Describes solution clarity (clear/turbid/cloudy)
- [ ] Notes color intensity or changes

**Example:** "Fine particles are barely visible... the solution remains mostly clear but shows initial turbidity"

### 3. Growth Estimation ✓
- [ ] Includes estimated growth percentage (0-100%)
- [ ] Percentage is within expected range for phase
- [ ] Matches visual appearance

**Expected Ranges:**
- Unsaturated: 0%
- Labile: 5-15%
- Intermediate: 15-50%
- Metastable: 50-100%

### 4. Process Context ✓
- [ ] Explains what stage of crystallization this represents
- [ ] References whether this is initial, growth, or equilibration phase
- [ ] Describes what happens next (if applicable)

**Example:** "Stage: Active controlled growth, crystals establishing structure"

### 5. Technical Accuracy ✓
- [ ] Uses correct crystallization terminology
- [ ] No contradictory statements
- [ ] References relevant concepts (supersaturation, nucleation, etc.)
- [ ] Scientifically sound

**Correct Terms:**
- Nucleation (not "nucleation" misspelled)
- Super-saturated (not "over-saturated")
- Meta-stable zone (not "metastable zone" or other variations)
- De-supersaturation (not "desupersaturation")

### 6. Clarity & Language ✓
- [ ] Well-written English (if English) or Thai (if Thai)
- [ ] Grammatically correct
- [ ] Logically organized
- [ ] No unnecessary jargon or unclear phrasing
- [ ] Professional tone maintained

### 7. Completeness ✓
- [ ] All required elements present (phase, visuals, growth, stage, context)
- [ ] No incomplete or unfinished sentences
- [ ] Sufficient detail without being too verbose

**Recommended Length:** 100-300 characters

### 8. Consistency ✓
- [ ] Caption style consistent with others
- [ ] Similar phases have similar structure/format
- [ ] Terminology consistent across all captions

---

## Phase-Specific Validation

### UNSATURATED Phase
Must include:
- [ ] Mention of clear/transparent liquid
- [ ] Absence of crystal particles
- [ ] Reference to under-saturation or stability
- [ ] 0% growth indication
- [ ] Mention of "initial stage" or "waiting to crystallize"

**Example Caption:**
```
UNSATURATED: Clear, transparent sugar solution with no visible crystal particles. 
The liquid is under-saturated and in stable equilibrium. No crystallization has occurred. 
Growth: 0%. Stage: Initial, awaiting supersaturation.
```

### LABILE Phase
Must include:
- [ ] Mention of nucleation or seed formation
- [ ] Very small or barely visible particles
- [ ] Reference to super-saturation
- [ ] 5-15% growth indication
- [ ] Note about "sensitivity" or "critical point"

**Example Caption:**
```
LABILE: Very small crystal nuclei beginning to form in the super-saturated solution. 
Fine particles are barely visible, indicating the nucleation boundary has been crossed. 
The solution remains mostly clear but shows initial turbidity. 
Growth: ~10%. Stage: Primary nucleation, seed formation initiated.
```

### INTERMEDIATE Phase
Must include:
- [ ] Mention of crystal growth or establishment
- [ ] Visible particles/crystals present
- [ ] Increasing cloudiness/turbidity
- [ ] 15-50% growth indication
- [ ] Reference to "controlled growth" or "active growth"

**Example Caption:**
```
INTERMEDIATE: Visible crystal growth with multiple nuclei developing. 
The solution is progressively becoming cloudy/turbid as crystals expand. 
Particle size is increasing noticeably, ranging from microscopic to small visible crystals. 
Growth: ~35%. Stage: Active controlled growth, crystals establishing structure.
```

### METASTABLE Phase
Must include:
- [ ] Mention of well-developed or mature crystals
- [ ] Significant saturation or concentration
- [ ] Clear, defined crystal structures
- [ ] 50-100% growth indication
- [ ] Reference to "equilibration" or "harvest-ready" or "stable"

**Example Caption:**
```
METASTABLE: Well-developed crystals fully formed and in stable growth phase. 
The solution is significantly saturated with mature crystal formations throughout. 
Color intensity is pronounced, indicating high solute concentration. 
Crystals show defined structure and size distribution. 
Growth: ~85%. Stage: Final equilibration, harvest-ready crystallization.
```

---

## Common Issues & Corrections

### Issue 1: Vague Descriptions
❌ **Wrong:** "The image shows some stuff in liquid"  
✓ **Correct:** "The solution contains visible crystal particles ranging from microscopic to small visible crystals"

### Issue 2: Incorrect Growth Percentages
❌ **Wrong:** "Labile phase with 40% growth"  
✓ **Correct:** "Labile phase with ~10% growth (early nucleation)" OR "Intermediate phase with ~40% growth"

### Issue 3: Missing Phase Identification
❌ **Wrong:** "Crystals are visible and growing with increased saturation"  
✓ **Correct:** "INTERMEDIATE: Crystals are visible and growing with increased saturation. Growth: ~30%."

### Issue 4: Contradictory Statements
❌ **Wrong:** "Clear solution with no particles, but many visible crystals"  
✓ **Correct:** "Mostly clear solution with very small barely visible crystal seeds just forming"

### Issue 5: Unclear Terminology
❌ **Wrong:** "Over-saturated solution with precipitation events"  
✓ **Correct:** "Super-saturated solution with crystal nuclei forming at the nucleation boundary"

---

## Validation Scoring

### Score Calculation
Assign points for each validated criterion:
- Phase Identification: 10 points
- Visual Description: 15 points
- Growth Estimation: 10 points
- Process Context: 10 points
- Technical Accuracy: 15 points
- Clarity & Language: 15 points
- Completeness: 10 points
- Consistency: 5 points

**Total: 90 points**

### Rating Scale
- **90-90 (100%):** Excellent - Ready to use
- **80-89 (89%):** Good - Minor revisions possible
- **70-79 (78%):** Acceptable - Should review
- **Below 70:** Needs Revision - Regenerate or manually correct

---

## Manual Review Process

### Step 1: Random Sampling
- [ ] Select 10-20% of captions randomly
- [ ] Ensure representation from all phases
- [ ] Mix of different LLM providers if multiple used

### Step 2: Cross-Verification
- [ ] Compare caption with actual image
- [ ] Verify phase classification accuracy
- [ ] Check if visual descriptions match reality
- [ ] Validate growth percentage estimates

### Step 3: Domain Expert Review
- [ ] Have crystallization expert review samples
- [ ] Note any common issues
- [ ] Identify patterns in errors
- [ ] Provide feedback for improvement

### Step 4: Statistical Analysis
- [ ] Calculate accuracy by phase
- [ ] Identify phases with higher error rates
- [ ] Compare LLM provider performance
- [ ] Document confidence scores

---

## Filtering & Correction

### Automatic Filtering
Remove captions that:
- [ ] Are empty or very short (<50 characters)
- [ ] Don't mention the phase name
- [ ] Have impossibly high growth percentages for their phase
- [ ] Contain obvious spelling errors

### Manual Correction
For questionable captions:
- [ ] Review with original image
- [ ] Edit for accuracy
- [ ] Document changes made
- [ ] Re-validate after editing

### Regeneration
For poor-quality captions:
- [ ] Regenerate using different LLM model
- [ ] Use improved prompt engineering
- [ ] Compare both versions
- [ ] Select the better caption

---

## Storage & Documentation

### Validation Results File
Create `captions_validation_results.json`:
```json
{
  "image_path": "path/to/image.jpg",
  "phase_label": "intermediate",
  "caption": "...",
  "validation_scores": {
    "phase_identification": 10,
    "visual_description": 15,
    "growth_estimation": 10,
    "process_context": 10,
    "technical_accuracy": 15,
    "clarity_language": 15,
    "completeness": 10,
    "consistency": 5
  },
  "total_score": 90,
  "validation_status": "approved",
  "reviewer_notes": "...",
  "reviewed_date": "2025-12-18",
  "reviewed_by": "..."
}
```

### Metadata Log
Track all validations with:
- Reviewer name
- Date reviewed
- Scores assigned
- Notes/corrections made
- Final decision (approved/reject/revise)

---

## Sign-Off

After all captions are validated:
- [ ] All captions scored
- [ ] Filtering completed
- [ ] Manual reviews done
- [ ] Statistical analysis performed
- [ ] Corrections implemented
- [ ] Final dataset ready
- [ ] Documentation complete

**Project Validation Complete:** ___________  
**Date:** ___________  
**Reviewer:** ___________  
**Approval:** ✓ Approved / ✗ Needs Changes

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-18
