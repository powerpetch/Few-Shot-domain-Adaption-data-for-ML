"""
Generate Comprehensive Dataset Metadata
Script to create metadata file tracking all captions through the pipeline.

Author: CEIPP Crystallization Dataset
Date: 2025-12-18
"""

import os
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

FILTER_OUTPUT = r"d:\user\CEIPP\Filter"


def load_json_file(file_path: str) -> Dict or List or None:
    """Load JSON file safely."""
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None


def generate_metadata() -> Dict:
    """Generate comprehensive metadata for dataset."""
    
    print("Generating comprehensive dataset metadata...\n")
    
    # Check what files exist
    all_captions = load_json_file(os.path.join(FILTER_OUTPUT, "all_initial_captions.json"))
    approved = load_json_file(os.path.join(FILTER_OUTPUT, "annotated_captions", "approved_captions.json"))
    revision = load_json_file(os.path.join(FILTER_OUTPUT, "annotated_captions", "revision_needed_captions.json"))
    rejected = load_json_file(os.path.join(FILTER_OUTPUT, "annotated_captions", "rejected_captions.json"))
    
    metadata = {
        "generation_info": {
            "generated_at": datetime.now().isoformat(),
            "pipeline_version": "1.0",
            "process": "initial_captions -> llm_verification -> filtering"
        },
        "phase_definitions": {
            "unsaturated": {
                "description": "Dense sugar/polymer solution below saturation point",
                "visual_markers": ["Clear/translucent solution", "No visible crystals", "High concentration"],
                "timeline_position": "Point A - Initial state"
            },
            "labile": {
                "description": "Initial seeding phase with nucleation beginning",
                "visual_markers": ["Initial crystal formation", "Low crystal density", "Nucleation visible"],
                "timeline_position": "Around Point B - Seeding phase"
            },
            "intermediate": {
                "description": "Active crystal growth phase transitioning through metastable zone",
                "visual_markers": ["Visible crystal growth", "Medium crystal density", "Ongoing crystallization"],
                "timeline_position": "Between Points B-C - Growth phase"
            },
            "metastable": {
                "description": "Fully seeded crystallization with complete crystal development",
                "visual_markers": ["High crystal density", "Large crystals", "Fully developed crystals"],
                "timeline_position": "Points C-D - Full development"
            }
        },
        "dataset_structure": {
            "materials": {
                "phy_sugar_db": "Physical Sugar (Dense Batch)",
                "phy_sugar_opr": "Physical Sugar (Operation)",
                "vir_polymer": "Virtual Polymer"
            },
            "phases": ["unsaturated", "labile", "intermediate", "metastable"]
        },
        "pipeline_status": {},
        "statistics": {}
    }
    
    # Step 1: Initial Captions Generated
    if all_captions:
        by_phase = {}
        by_material = {}
        for cap in all_captions:
            phase = cap.get("phase")
            material = cap.get("material_type")
            
            if phase not in by_phase:
                by_phase[phase] = 0
            by_phase[phase] += 1
            
            if material not in by_material:
                by_material[material] = 0
            by_material[material] += 1
        
        metadata["pipeline_status"]["step_1_initial_captions"] = {
            "status": "COMPLETED",
            "total_captions": len(all_captions),
            "by_phase": by_phase,
            "by_material": by_material,
            "timestamp": datetime.now().isoformat()
        }
        print(f"✓ Step 1: Generated {len(all_captions)} initial captions")
    
    # Step 2: LLM Verification (check if batch was prepared)
    batch_prompts = load_json_file(os.path.join(FILTER_OUTPUT, "llm_verification_logs", "batch_prompts.json"))
    if batch_prompts:
        metadata["pipeline_status"]["step_2_llm_verification"] = {
            "status": "PREPARED",
            "batch_id": batch_prompts.get("batch_id"),
            "total_prompts": batch_prompts.get("total_images", 0),
            "batch_created_at": batch_prompts.get("created_at"),
            "next_action": "Send batch_prompts.json/txt to multi-modal LLM for verification"
        }
        print(f"✓ Step 2: LLM verification batch prepared for {batch_prompts.get('total_images', 0)} images")
    
    # Step 3: Filtering Results
    has_results = False
    if approved or revision or rejected:
        has_results = True
        total_processed = (len(approved) if approved else 0) + \
                         (len(revision) if revision else 0) + \
                         (len(rejected) if rejected else 0)
        
        approval_rate = 0
        if total_processed > 0:
            approval_rate = (len(approved) if approved else 0) / total_processed * 100
        
        metadata["pipeline_status"]["step_3_filtering"] = {
            "status": "COMPLETED",
            "total_processed": total_processed,
            "approved": len(approved) if approved else 0,
            "revision_needed": len(revision) if revision else 0,
            "rejected": len(rejected) if rejected else 0,
            "approval_rate": f"{approval_rate:.1f}%",
            "timestamp": datetime.now().isoformat()
        }
        print(f"✓ Step 3: Filtering complete")
        print(f"  - Approved: {len(approved) if approved else 0}")
        print(f"  - Revision Needed: {len(revision) if revision else 0}")
        print(f"  - Rejected: {len(rejected) if rejected else 0}")
    
    # Overall Statistics
    if all_captions:
        metadata["statistics"]["total_images_in_dataset"] = len(all_captions)
        metadata["statistics"]["ready_for_training"] = len(approved) if approved else 0
        metadata["statistics"]["pending_review"] = len(revision) if revision else 0
        metadata["statistics"]["flagged_for_review"] = len(rejected) if rejected else 0
        
        if has_results:
            total_ready = (len(approved) if approved else 0) + (len(revision) if revision else 0)
            metadata["statistics"]["coverage_percentage"] = f"{(total_ready / len(all_captions) * 100):.1f}%" if len(all_captions) > 0 else "0%"
    
    # Add workflow instructions
    metadata["next_steps"] = []
    if not batch_prompts:
        metadata["next_steps"].append({
            "order": 1,
            "action": "Generate LLM verification batch",
            "command": "python prepare_llm_batch.py",
            "output": "batch_prompts.json, batch_prompts.txt"
        })
    
    if not has_results and batch_prompts:
        metadata["next_steps"].append({
            "order": 2,
            "action": "Send batch to multi-modal LLM",
            "details": "Use batch_prompts.txt or batch_prompts.json with GPT-4V, Claude Vision, Gemini, etc.",
            "save_as": "llm_verification_logs/llm_responses.json"
        })
    
    if batch_prompts and not has_results:
        metadata["next_steps"].append({
            "order": 3,
            "action": "Filter LLM responses",
            "command": "python filter_llm_responses.py",
            "input": "llm_verification_logs/llm_responses.json",
            "output": "approved_captions.json, revision_needed_captions.json, rejected_captions.json"
        })
    
    if has_results:
        metadata["next_steps"].append({
            "order": 4,
            "action": "Review and apply revisions",
            "details": "Manually review revision_needed_captions.json and rejected_captions.json",
            "next": "Re-run filter if major changes made"
        })
    
    return metadata


def save_metadata(metadata: Dict) -> None:
    """Save metadata to file."""
    
    metadata_file = os.path.join(FILTER_OUTPUT, "dataset_metadata.json")
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved: {metadata_file}")


def create_pipeline_status_report(metadata: Dict) -> None:
    """Create human-readable pipeline status report."""
    
    report_file = os.path.join(FILTER_OUTPUT, "PIPELINE_STATUS.md")
    
    report = f"""# Crystallization Dataset - Captioning Pipeline Status

**Last Updated**: {datetime.now().isoformat()}

## Pipeline Overview

```
Initial Captions → LLM Verification → Filtering → Ready for Training
     ↓                   ↓                  ↓
  Step 1              Step 2            Step 3
```

## Current Status

"""
    
    # Add status for each step
    for step_name, step_data in metadata.get("pipeline_status", {}).items():
        status = step_data.get("status")
        emoji = "✅" if status == "COMPLETED" else "🔄" if status == "PREPARED" else "⏳"
        
        report += f"\n### {step_name.replace('step_', 'Step ').replace('_', ' ')}: {emoji} {status}\n\n"
        
        if step_name == "step_1_initial_captions":
            report += f"- Total Captions: {step_data.get('total_captions', 0)}\n"
            report += "- By Phase:\n"
            for phase, count in step_data.get('by_phase', {}).items():
                report += f"  - {phase.upper()}: {count}\n"
            report += "- By Material:\n"
            for material, count in step_data.get('by_material', {}).items():
                report += f"  - {material}: {count}\n"
        
        elif step_name == "step_2_llm_verification":
            report += f"- Batch ID: {step_data.get('batch_id', 'N/A')}\n"
            report += f"- Total Prompts: {step_data.get('total_prompts', 0)}\n"
            report += f"- Batch Created: {step_data.get('batch_created_at', 'N/A')}\n"
            report += f"- Next Action: {step_data.get('next_action', 'N/A')}\n"
        
        elif step_name == "step_3_filtering":
            report += f"- Total Processed: {step_data.get('total_processed', 0)}\n"
            report += f"- Approved: {step_data.get('approved', 0)}\n"
            report += f"- Revision Needed: {step_data.get('revision_needed', 0)}\n"
            report += f"- Rejected: {step_data.get('rejected', 0)}\n"
            report += f"- Approval Rate: {step_data.get('approval_rate', 'N/A')}\n"
    
    # Add statistics
    report += "\n## Statistics\n\n"
    for stat_name, stat_value in metadata.get("statistics", {}).items():
        report += f"- {stat_name.replace('_', ' ').title()}: {stat_value}\n"
    
    # Add next steps
    report += "\n## Next Steps\n\n"
    next_steps = metadata.get("next_steps", [])
    if not next_steps:
        report += "✅ All steps completed! Dataset is ready for training.\n"
    else:
        for step in next_steps:
            report += f"**{step.get('order')}. {step.get('action')}**\n"
            if 'command' in step:
                report += f"   Command: `{step['command']}`\n"
            if 'details' in step:
                report += f"   Details: {step['details']}\n"
            if 'input' in step:
                report += f"   Input: {step['input']}\n"
            if 'output' in step:
                report += f"   Output: {step['output']}\n"
            report += "\n"
    
    # Add file structure
    report += "\n## Output File Structure\n\n"
    report += """```
Filter/
├── README.md
├── generate_initial_captions.py
├── prepare_llm_batch.py
├── filter_llm_responses.py
├── generate_metadata.py (this script)
├── all_initial_captions.json
├── dataset_metadata.json
├── generation_statistics.json
├── captioning_summary.txt
├── filtering_statistics.json
├── filtering_report.txt
├── PIPELINE_STATUS.md (this file)
├── annotated_captions/
│   ├── unsaturated_captions.json
│   ├── labile_captions.json
│   ├── intermediate_captions.json
│   ├── metastable_captions.json
│   ├── approved_captions.json (ready for training)
│   ├── revision_needed_captions.json
│   ├── rejected_captions.json
│   └── unprocessed_captions.json
└── llm_verification_logs/
    ├── batch_prompts.json
    ├── batch_prompts.txt
    ├── llm_responses.json
    ├── INSTRUCTIONS.md
    └── RESPONSE_TEMPLATE.json
```
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ Saved: {report_file}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("Generating Comprehensive Dataset Metadata")
    print("=" * 70)
    print()
    
    # Generate metadata
    metadata = generate_metadata()
    
    # Save metadata
    save_metadata(metadata)
    
    # Create status report
    create_pipeline_status_report(metadata)
    
    print("\n" + "=" * 70)
    print("✓ Metadata generation complete!")
    print("=" * 70)
    print("\nDocumentation:")
    print("- dataset_metadata.json: Complete metadata in JSON format")
    print("- PIPELINE_STATUS.md: Human-readable pipeline status")
    print("=" * 70)


if __name__ == "__main__":
    main()
