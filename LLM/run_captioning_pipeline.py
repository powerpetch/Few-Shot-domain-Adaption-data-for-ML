"""
Complete Pipeline Runner for Crystallization Dataset Captioning & Verification
===============================================================================
This script orchestrates the entire workflow:
1. Generate enhanced captions with growth percentages
2. Run LLM verification using BLIP-2
3. Filter and analyze results
4. Generate final annotated dataset

Usage:
    python run_captioning_pipeline.py --mode all
    python run_captioning_pipeline.py --mode captions_only
    python run_captioning_pipeline.py --mode verify_only
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_PATH = Path(__file__).parent.parent  # CEIPP folder
LLM_PATH = Path(__file__).parent  # LLM folder
FILTER_PATH = BASE_PATH / "Filter"
DATASET_ROOT = BASE_PATH / "_21p1_pjirayu_Seed-Crystallization-Dataset" / "balanced_crystallization"

OUTPUT_FILES = {
    "captions_v2": FILTER_PATH / "all_captions_VER2.json",
    "verification_prompts": LLM_PATH / "llm_verification_results" / "verification_prompts_prepared.json",
    "verification_results": LLM_PATH / "llm_verification_results" / "verification_results.json",
    "filtered_captions": LLM_PATH / "filtered_captions_final.json",
    "needs_review": LLM_PATH / "llm_verification_results" / "needs_review.json"
}

# =============================================================================
# STEP 1: CAPTION GENERATION
# =============================================================================

def run_caption_generation():
    """Run the enhanced caption generation."""
    print("\n" + "=" * 80)
    print("STEP 1: Enhanced Caption Generation")
    print("=" * 80)
    
    try:
        from Filter.generate_captions_VER2 import process_dataset, save_captions
        
        captions, statistics = process_dataset()
        
        if captions:
            save_captions(captions, statistics)
            print(f"\n[SUCCESS] Generated {len(captions)} captions")
            return True
        else:
            print("[WARNING] No captions generated")
            return False
            
    except ImportError as e:
        print(f"[ERROR] Failed to import caption generator: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Caption generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# =============================================================================
# STEP 2: PREPARE VERIFICATION PROMPTS
# =============================================================================

def prepare_verification_prompts():
    """Generate verification prompts without running the model."""
    print("\n" + "=" * 80)
    print("STEP 2: Prepare LLM Verification Prompts")
    print("=" * 80)
    
    try:
        from llm_verification import generate_verification_prompts_only
        
        result = generate_verification_prompts_only()
        
        if result:
            print(f"\n[SUCCESS] Prepared prompts for {result.get('total_images', 0)} images")
            return True
        return False
        
    except ImportError as e:
        print(f"[ERROR] Failed to import verification module: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Prompt preparation failed: {e}")
        return False

# =============================================================================
# STEP 3: RUN LLM VERIFICATION (Optional - requires GPU)
# =============================================================================

def run_llm_verification(model_name: str = "blip2_opt", sample_size: int = None):
    """Run full LLM verification on captions."""
    print("\n" + "=" * 80)
    print("STEP 3: LLM Verification (BLIP-2)")
    print("=" * 80)
    
    try:
        import torch
        if torch.cuda.is_available():
            print(f"[INFO] CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            print("[WARNING] CUDA not available. Using CPU (will be slow).")
            
    except ImportError:
        print("[ERROR] PyTorch not installed. Install with: pip install torch")
        return False
    
    try:
        from llm_verification import run_batch_verification
        
        results, statistics = run_batch_verification(
            model_name=model_name,
            sample_size=sample_size
        )
        
        if results:
            print(f"\n[SUCCESS] Verified {len(results)} images")
            return True
        return False
        
    except Exception as e:
        print(f"[ERROR] LLM verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# =============================================================================
# STEP 4: FILTER AND ANALYZE RESULTS
# =============================================================================

def filter_and_analyze_results():
    """Analyze verification results and filter captions."""
    print("\n" + "=" * 80)
    print("STEP 4: Filter and Analyze Results")
    print("=" * 80)
    
    verification_results_file = OUTPUT_FILES["verification_results"]
    captions_file = OUTPUT_FILES["captions_v2"]
    
    if not verification_results_file.exists():
        print("[INFO] No verification results found. Skipping filtering.")
        return True
    
    # Load data
    with open(verification_results_file, 'r', encoding='utf-8') as f:
        verification_results = json.load(f)
    
    with open(captions_file, 'r', encoding='utf-8') as f:
        captions = json.load(f)
    
    # Create lookup dict
    verification_lookup = {
        r.get("image_name", ""): r for r in verification_results
    }
    
    # Merge and filter
    filtered_captions = []
    needs_review = []
    
    for caption in captions:
        image_name = caption.get("image", "")
        verification = verification_lookup.get(image_name, {})
        
        # Add verification results to caption
        caption["llm_verification"] = verification.get("verification_results", {})
        caption["verification_summary"] = verification.get("verification_summary", {})
        
        # Check if needs review
        if verification.get("verification_summary", {}).get("needs_review"):
            caption["llm_verification_status"] = "needs_review"
            needs_review.append(caption)
        elif verification.get("verification_summary", {}).get("phase_match"):
            caption["llm_verification_status"] = "verified"
        else:
            caption["llm_verification_status"] = "unverified"
        
        filtered_captions.append(caption)
    
    # Save filtered captions
    output_file = OUTPUT_FILES["filtered_captions"]
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_captions, f, indent=2, ensure_ascii=False)
    print(f"[OK] Filtered captions saved to: {output_file}")
    
    # Statistics
    verified_count = sum(1 for c in filtered_captions if c.get("llm_verification_status") == "verified")
    needs_review_count = len(needs_review)
    
    print(f"\n[STATS] Total captions: {len(filtered_captions)}")
    print(f"[STATS] Verified: {verified_count}")
    print(f"[STATS] Needs review: {needs_review_count}")
    
    return True

# =============================================================================
# STEP 5: GENERATE FINAL REPORT
# =============================================================================

def generate_final_report():
    """Generate a summary report of the entire pipeline."""
    print("\n" + "=" * 80)
    print("STEP 5: Generate Final Report")
    print("=" * 80)
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "pipeline_steps": [],
        "statistics": {},
        "output_files": {}
    }
    
    # Check each output file
    for name, path in OUTPUT_FILES.items():
        if path.exists():
            report["output_files"][name] = {
                "path": str(path),
                "exists": True,
                "size_bytes": path.stat().st_size
            }
            
            # Load and add stats for JSON files
            if path.suffix == '.json':
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        report["output_files"][name]["item_count"] = len(data)
                except:
                    pass
        else:
            report["output_files"][name] = {"path": str(path), "exists": False}
    
    # Check captions statistics
    if OUTPUT_FILES["captions_v2"].exists():
        with open(OUTPUT_FILES["captions_v2"], 'r', encoding='utf-8') as f:
            captions = json.load(f)
        
        report["statistics"]["total_captions"] = len(captions)
        report["statistics"]["by_phase"] = {}
        report["statistics"]["by_material"] = {}
        
        for caption in captions:
            phase = caption.get("phase", "unknown")
            material = caption.get("category_id", "unknown")
            
            report["statistics"]["by_phase"][phase] = report["statistics"]["by_phase"].get(phase, 0) + 1
            report["statistics"]["by_material"][material] = report["statistics"]["by_material"].get(material, 0) + 1
    
    # Save report
    report_file = FILTER_PATH / "pipeline_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Report saved to: {report_file}")
    
    # Print summary
    print("\n" + "-" * 80)
    print("PIPELINE SUMMARY")
    print("-" * 80)
    
    if "total_captions" in report["statistics"]:
        print(f"Total Captions: {report['statistics']['total_captions']}")
        print("\nBy Phase:")
        for phase, count in report["statistics"]["by_phase"].items():
            print(f"  {phase:15}: {count:4}")
        print("\nBy Material:")
        for material, count in report["statistics"]["by_material"].items():
            print(f"  {material:20}: {count:4}")
    
    return True

# =============================================================================
# MAIN PIPELINE
# =============================================================================

def run_pipeline(
    mode: str = "all",
    model_name: str = "blip2_opt",
    sample_size: int = None
):
    """
    Run the complete pipeline or specific steps.
    
    Args:
        mode: 'all', 'captions_only', 'verify_only', 'prompts_only'
        model_name: BLIP-2 model variant to use
        sample_size: Number of samples for verification (None = all)
    """
    print("=" * 80)
    print("CRYSTALLIZATION DATASET CAPTIONING & VERIFICATION PIPELINE")
    print("=" * 80)
    print(f"Mode: {mode}")
    print(f"Dataset: {DATASET_ROOT}")
    print(f"Output: {FILTER_PATH}")
    print("=" * 80)
    
    success = True
    
    if mode in ["all", "captions_only"]:
        success = run_caption_generation() and success
    
    if mode in ["all", "prompts_only"]:
        success = prepare_verification_prompts() and success
    
    if mode in ["all", "verify_only"]:
        success = run_llm_verification(model_name, sample_size) and success
    
    if mode == "all":
        success = filter_and_analyze_results() and success
        success = generate_final_report() and success
    
    print("\n" + "=" * 80)
    if success:
        print("[PIPELINE COMPLETE] All steps finished successfully!")
    else:
        print("[PIPELINE INCOMPLETE] Some steps had errors. Check logs above.")
    print("=" * 80)
    
    return success

# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Crystallization Dataset Captioning & Verification Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_captioning_pipeline.py --mode all
    python run_captioning_pipeline.py --mode captions_only
    python run_captioning_pipeline.py --mode verify_only --model blip2_flan --sample 100
    python run_captioning_pipeline.py --mode prompts_only
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["all", "captions_only", "verify_only", "prompts_only"],
        default="all",
        help="Pipeline mode (default: all)"
    )
    
    parser.add_argument(
        "--model",
        default="blip2_opt",
        choices=["blip2_opt", "blip2_flan", "blip2_opt_6.7b"],
        help="BLIP-2 model variant (default: blip2_opt)"
    )
    
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Number of samples for verification (default: all)"
    )
    
    args = parser.parse_args()
    
    success = run_pipeline(
        mode=args.mode,
        model_name=args.model,
        sample_size=args.sample
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
