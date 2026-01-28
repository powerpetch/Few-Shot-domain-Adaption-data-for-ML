"""
Prepare Batch Prompts for Multi-Modal LLM Verification
Script to format captions for sending to multi-modal LLM with proper structure.

Author: CEIPP Crystallization Dataset
Date: 2025-12-18
"""

import os
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

FILTER_OUTPUT = r"d:\user\CEIPP\Filter"


def load_captions(captions_file: str) -> List[Dict]:
    """Load initial captions from JSON file."""
    try:
        with open(captions_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ Error: File not found: {captions_file}")
        print("  Please run generate_initial_captions.py first")
        return []


def create_llm_batch_prompt(caption_data: Dict) -> str:
    """Create formatted prompt for multi-modal LLM."""
    
    template = f"""[CRYSTALLIZATION IMAGE VERIFICATION REQUEST]
Image ID: {caption_data['image']}
Material: {caption_data['material_name']}
Phase Classification: {caption_data['phase'].upper()}

Dataset Phase Definition:
{caption_data['phase_description']}

Initial Caption:
"{caption_data['initial_caption']}"

Expected Visual Markers:
{', '.join(caption_data['visual_markers'])}

=== VERIFICATION QUESTIONS ===

1. **Phase Accuracy**: Does the image clearly represent the {caption_data['phase'].upper()} phase?
   - Confidence level (0-100%):
   - Key visual indicators observed:

2. **Caption Completeness**: Does the caption adequately describe:
   a) The crystallization phase?
   b) Observable crystal characteristics?
   c) Progression stage in the crystallization timeline?
   (Yes/No for each, with notes)

3. **Technical Accuracy**: Are there any scientific inaccuracies or missing technical details?
   - Issues found:
   - Suggested improvements:

4. **Crystal Growth Metrics**: Can you estimate or identify any growth characteristics?
   - Crystal density level:
   - Approximate crystal size progression:
   - Saturation state indicators:

5. **Cross-Phase Verification**: How confident are you this is NOT one of the other phases?
   - Could it be Unsaturated? (Why/Why not)
   - Could it be Labile? (Why/Why not)
   - Could it be Intermediate? (Why/Why not)
   - Could it be Metastable? (Why/Why not)

6. **Final Recommendation**:
   - Classification Confidence: ___/100
   - Caption Status: [APPROVE / REVISION NEEDED / REJECT]
   - Recommended Revision:

=== END VERIFICATION ===
"""
    return template


def create_batch_verification_file(captions: List[Dict], sample_size: int = None) -> None:
    """Create batch file with verification prompts for LLM."""
    
    if sample_size and sample_size < len(captions):
        print(f"Creating batch for {sample_size} sample images (out of {len(captions)} total)")
        captions = captions[:sample_size]
    else:
        print(f"Creating batch for all {len(captions)} images")
    
    batch_data = {
        "batch_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "total_images": len(captions),
        "created_at": datetime.now().isoformat(),
        "instructions": """
Process each image with the following steps:
1. Visually analyze the image
2. Determine if it matches the stated crystallization phase
3. Answer all verification questions thoroughly
4. Provide confidence level and recommendation
5. For revision needed items, explain specific changes required
""",
        "verification_prompts": []
    }
    
    for idx, caption_data in enumerate(captions, 1):
        prompt = create_llm_batch_prompt(caption_data)
        batch_data["verification_prompts"].append({
            "index": idx,
            "image_id": caption_data["image"],
            "phase": caption_data["phase"],
            "material": caption_data["material_type"],
            "prompt": prompt
        })
    
    # Save as JSON for programmatic processing
    batch_json_file = os.path.join(FILTER_OUTPUT, "llm_verification_logs", "batch_prompts.json")
    os.makedirs(os.path.dirname(batch_json_file), exist_ok=True)
    
    with open(batch_json_file, 'w', encoding='utf-8') as f:
        json.dump(batch_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved: {batch_json_file}")
    
    # Save as readable text file for manual review
    batch_txt_file = os.path.join(FILTER_OUTPUT, "llm_verification_logs", "batch_prompts.txt")
    with open(batch_txt_file, 'w', encoding='utf-8') as f:
        f.write("MULTI-MODAL LLM VERIFICATION BATCH\n")
        f.write("=" * 80 + "\n")
        f.write(f"Batch ID: {batch_data['batch_id']}\n")
        f.write(f"Total Images: {len(captions)}\n")
        f.write(f"Created: {batch_data['created_at']}\n")
        f.write("\n" + batch_data['instructions'] + "\n")
        f.write("=" * 80 + "\n\n")
        
        for item in batch_data["verification_prompts"]:
            f.write(f"\n{'#' * 80}\n")
            f.write(f"IMAGE {item['index']}/{len(captions)}\n")
            f.write(f"{'#' * 80}\n")
            f.write(item['prompt'])
            f.write("\n")
    print(f"✓ Saved: {batch_txt_file}")


def create_summary_instruction() -> None:
    """Create instruction file for LLM verification process."""
    
    instruction_file = os.path.join(FILTER_OUTPUT, "llm_verification_logs", "INSTRUCTIONS.md")
    os.makedirs(os.path.dirname(instruction_file), exist_ok=True)
    
    instruction_content = """# Multi-Modal LLM Verification Instructions

## Overview
This batch contains crystallization images classified into 4 phases. Each image has an initial caption that needs verification against actual visual content.

## Phase Definitions

### Unsaturated
- Dense sugar/polymer solution
- No crystal nucleation occurs
- System is below saturation point
- Visual: Clear/translucent, no visible crystals

### Labile  
- Crystal nucleation has begun
- Initial seeding phase
- Preparation for growth
- Visual: Initial crystals visible, low density

### Intermediate
- Active crystal growth occurring
- Transition between labile and metastable zones
- Crystal size increasing
- Visual: Medium crystal density, visible growth

### Metastable
- Fully seeded crystallization
- Complete crystal development
- Maximum growth achieved
- Visual: High crystal density, fully developed crystals

## Verification Process

For each image:

1. **Examine Image Carefully**
   - Look at crystal density and size
   - Note clarity/translucency level
   - Identify concentration indicators
   - Check for nucleation or growth

2. **Answer Verification Questions**
   - Be specific about visual observations
   - Provide confidence percentages
   - List key indicators observed
   - Compare against other phase characteristics

3. **Evaluate Caption**
   - Check if it accurately describes what you see
   - Identify missing details
   - Note any inaccuracies
   - Suggest improvements

4. **Provide Recommendation**
   - Mark as APPROVE if confident
   - Mark as REVISION NEEDED if minor fixes required
   - Mark as REJECT if phase is wrong or caption is inaccurate

## Output Format

For each verification, provide:

```json
{
  "image_id": "filename.jpg",
  "phase": "phase_name",
  "confidence": 85,
  "status": "APPROVE|REVISION_NEEDED|REJECT",
  "visual_observations": "detailed description",
  "caption_issues": ["issue1", "issue2"],
  "suggested_caption": "revised caption if needed",
  "notes": "additional comments"
}
```

## Important Notes

- Base classification on VISUAL EVIDENCE only
- Reference the 4 phase definitions provided
- Be specific about what you observe
- Document all discrepancies
- Flag any images that don't clearly fit a phase

## When to Mark as REVISION NEEDED vs REJECT

**REVISION NEEDED**: Caption is mostly correct but needs refinement
- Minor detail corrections
- Missing specific observation
- Slight wording improvement needed

**REJECT**: Phase classification or caption is fundamentally wrong
- Image belongs to different phase
- Caption contradicts visual content
- Cannot determine phase from image

---

Please process all images and save responses in a structured format.
"""
    
    with open(instruction_file, 'w', encoding='utf-8') as f:
        f.write(instruction_content)
    print(f"✓ Saved: {instruction_file}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("Preparing LLM Verification Batch")
    print("=" * 70)
    
    # Load captions
    captions_file = os.path.join(FILTER_OUTPUT, "all_initial_captions.json")
    captions = load_captions(captions_file)
    
    if not captions:
        return
    
    print(f"\n✓ Loaded {len(captions)} captions\n")
    
    # Create batch prompts
    print("Creating batch verification prompts...")
    create_batch_verification_file(captions)
    
    # Create instructions
    print("Creating verification instructions...")
    create_summary_instruction()
    
    print("\n" + "=" * 70)
    print("✓ Batch preparation complete!")
    print("=" * 70)
    print("\nNext Steps:")
    print("1. Use batch_prompts.json or batch_prompts.txt")
    print("2. Send images + prompts to multi-modal LLM (GPT-4V, Claude, Gemini, etc.)")
    print("3. Collect LLM responses in the format specified")
    print("4. Run filter_llm_responses.py with LLM feedback")
    print("\nDocumentation:")
    print("- See INSTRUCTIONS.md for detailed verification guidelines")
    print("=" * 70)


if __name__ == "__main__":
    main()
