"""
Master Execution Script for Captioning Pipeline
Orchestrates the complete workflow from image analysis to filtered captions.

Author: CEIPP Crystallization Dataset
Date: 2025-12-18
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

FILTER_OUTPUT = r"d:\user\CEIPP\Filter"


def run_script(script_name: str, description: str) -> bool:
    """Run a Python script and handle errors."""
    script_path = os.path.join(FILTER_OUTPUT, script_name)
    
    print("\n" + "=" * 70)
    print(f"STEP: {description}")
    print("=" * 70)
    
    if not os.path.exists(script_path):
        print(f"✗ Script not found: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=FILTER_OUTPUT,
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Error running script: {e}")
        return False


def show_menu() -> str:
    """Display interactive menu."""
    menu = """
╔════════════════════════════════════════════════════════════════════╗
║   CRYSTALLIZATION DATASET CAPTIONING PIPELINE                      ║
║   Multi-Modal LLM Verification Workflow                            ║
╚════════════════════════════════════════════════════════════════════╝

AVAILABLE COMMANDS:

  1. generate_captions    - Generate initial captions from images
  2. prepare_batch        - Prepare LLM verification batch
  3. filter_responses     - Filter LLM responses and create final captions
  4. generate_metadata    - Generate comprehensive metadata report
  5. run_all              - Run complete pipeline (1→2→3→4)
  6. status               - Show pipeline status
  7. help                 - Show detailed help
  8. exit                 - Exit program

Enter command number (1-8): """
    return menu


def show_help():
    """Show detailed help information."""
    help_text = """
╔════════════════════════════════════════════════════════════════════╗
║                    PIPELINE WORKFLOW GUIDE                         ║
╚════════════════════════════════════════════════════════════════════╝

OVERVIEW
────────
This pipeline creates captions for crystallization images with 
multi-modal LLM verification and cross-validation.

WORKFLOW STEPS
──────────────

Step 1: GENERATE INITIAL CAPTIONS (Command: 1)
   Input:  Images from balanced_crystallization dataset
   Output: all_initial_captions.json
   
   This step:
   - Scans all crystallization images
   - Classifies by phase (unsaturated, labile, intermediate, metastable)
   - Creates template-based captions for each image
   - Generates statistics

Step 2: PREPARE LLM VERIFICATION BATCH (Command: 2)
   Input:  all_initial_captions.json
   Output: batch_prompts.json, batch_prompts.txt
   
   This step:
   - Creates structured prompts for multi-modal LLM
   - Prepares verification questions
   - Generates instruction file for LLM
   - Creates response template

Step 3: SEND TO MULTI-MODAL LLM (Manual Step)
   Tools: GPT-4V, Claude Vision, Gemini, or similar
   
   This step (manual):
   - Use batch_prompts.txt or batch_prompts.json
   - Send images + prompts to LLM
   - Collect LLM feedback on accuracy and completeness
   - Save responses in llm_verification_logs/llm_responses.json

Step 4: FILTER RESPONSES (Command: 3)
   Input:  all_initial_captions.json + llm_responses.json
   Output: approved_captions.json, revision_needed_captions.json, etc.
   
   This step:
   - Processes LLM feedback
   - Categorizes captions (Approved/Revision/Rejected/Unprocessed)
   - Applies suggested revisions
   - Generates filtering statistics

Step 5: GENERATE METADATA (Command: 4)
   Input:  Results from all previous steps
   Output: dataset_metadata.json, PIPELINE_STATUS.md
   
   This step:
   - Creates comprehensive metadata
   - Tracks pipeline progress
   - Documents dataset structure
   - Provides next action recommendations

USAGE EXAMPLES
──────────────

Option A: Run complete pipeline automatically
   Command: 5 (run_all)
   
Option B: Run step by step
   Command: 1 → Wait for LLM verification → Command: 3 → Command: 4
   
Option C: Check progress anytime
   Command: 6 (status)

OUTPUT STRUCTURE
────────────────

Filter/
├── all_initial_captions.json              (Step 1 output)
├── generation_statistics.json
├── captioning_summary.txt
├── llm_verification_logs/
│   ├── batch_prompts.json                (Step 2 output)
│   ├── batch_prompts.txt
│   ├── INSTRUCTIONS.md
│   ├── RESPONSE_TEMPLATE.json
│   └── llm_responses.json                (Step 3 input - manual)
├── annotated_captions/
│   ├── approved_captions.json            (Step 4 output)
│   ├── revision_needed_captions.json
│   ├── rejected_captions.json
│   └── unprocessed_captions.json
├── dataset_metadata.json                 (Step 5 output)
├── PIPELINE_STATUS.md
└── filtering_statistics.json

IMPORTANT NOTES
───────────────

1. Phase Definitions:
   - UNSATURATED: Dense solution, no crystals (Point A)
   - LABILE: Nucleation begun, low crystal density (Around Point B)
   - INTERMEDIATE: Active growth, medium density (Between B-C)
   - METASTABLE: Full development, high density (Points C-D)

2. LLM Verification:
   - Always reference the 4 phase definitions
   - Use LLM to validate, not replace class definitions
   - Document any discrepancies found

3. Quality Control:
   - Approved captions ready for training
   - Revision needed: apply suggested fixes, re-verify if major
   - Rejected: manual reclassification may be needed

WORKFLOW DIAGRAM
────────────────

[Dataset Images]
       ↓
[1. Generate Captions]
       ↓
[all_initial_captions.json]
       ↓
[2. Prepare LLM Batch]
       ↓
[batch_prompts.json/txt]
       ↓
[3. Manual: Send to Multi-Modal LLM] ← GPT-4V, Claude, Gemini, etc.
       ↓
[llm_responses.json]
       ↓
[4. Filter Responses]
       ↓
[approved_captions.json] → Ready for Training!
[revision_needed_captions.json] → Manual Review
[rejected_captions.json] → Reclassify
       ↓
[5. Generate Metadata]
       ↓
[dataset_metadata.json, PIPELINE_STATUS.md]

"""
    print(help_text)


def show_status():
    """Show current pipeline status."""
    print("\n" + "=" * 70)
    print("PIPELINE STATUS")
    print("=" * 70)
    
    # Check for key files
    checks = {
        "Step 1 - Initial Captions": "all_initial_captions.json",
        "Step 2 - LLM Batch": "llm_verification_logs/batch_prompts.json",
        "Step 3 - LLM Responses": "llm_verification_logs/llm_responses.json",
        "Step 4 - Filtered Results": "annotated_captions/approved_captions.json",
        "Step 5 - Metadata": "dataset_metadata.json"
    }
    
    for step_name, file_path in checks.items():
        full_path = os.path.join(FILTER_OUTPUT, file_path)
        if os.path.exists(full_path):
            size_kb = os.path.getsize(full_path) / 1024
            print(f"✓ {step_name:35} {size_kb:8.1f} KB")
        else:
            print(f"✗ {step_name:35} Not Ready")
    
    # Check metadata
    metadata_file = os.path.join(FILTER_OUTPUT, "dataset_metadata.json")
    if os.path.exists(metadata_file):
        print("\n" + "-" * 70)
        print("DETAILED STATUS:")
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            for step_name, step_data in metadata.get("pipeline_status", {}).items():
                status = step_data.get("status")
                print(f"\n{step_name.replace('step_', 'Step ').replace('_', ' ')}: {status}")
                if "total_captions" in step_data:
                    print(f"  Total: {step_data['total_captions']}")
                if "total_processed" in step_data:
                    print(f"  Processed: {step_data['total_processed']}")
                if "approved" in step_data:
                    print(f"  Approved: {step_data['approved']}")
        except:
            pass
    
    print("\n" + "=" * 70)


def main():
    """Main interactive menu."""
    print("\nInitializing Captioning Pipeline...")
    print(f"Working Directory: {FILTER_OUTPUT}\n")
    
    while True:
        menu = show_menu()
        choice = input(menu).strip()
        
        if choice == "1":
            print("\n→ Generating initial captions from images...")
            run_script("generate_initial_captions.py", "Generate Initial Captions")
        
        elif choice == "2":
            print("\n→ Preparing LLM verification batch...")
            run_script("prepare_llm_batch.py", "Prepare LLM Batch")
        
        elif choice == "3":
            print("\n→ Filtering LLM responses...")
            run_script("filter_llm_responses.py", "Filter LLM Responses")
        
        elif choice == "4":
            print("\n→ Generating metadata...")
            run_script("generate_metadata.py", "Generate Metadata")
        
        elif choice == "5":
            print("\n→ Running complete pipeline...")
            print("This will execute steps 1-4 in sequence\n")
            if input("Continue? (y/n): ").lower() == 'y':
                run_script("generate_initial_captions.py", "Step 1: Generate Initial Captions")
                run_script("prepare_llm_batch.py", "Step 2: Prepare LLM Batch")
                print("\n⚠ Manual Step Required:")
                print("  Please send images + batch_prompts to multi-modal LLM")
                print("  Save responses to: llm_verification_logs/llm_responses.json")
                input("Press Enter when LLM verification is complete...")
                run_script("filter_llm_responses.py", "Step 3: Filter LLM Responses")
                run_script("generate_metadata.py", "Step 4: Generate Metadata")
        
        elif choice == "6":
            show_status()
        
        elif choice == "7":
            show_help()
        
        elif choice == "8":
            print("\n✓ Exiting pipeline. Goodbye!")
            break
        
        else:
            print("✗ Invalid command. Please enter 1-8.")


if __name__ == "__main__":
    main()
