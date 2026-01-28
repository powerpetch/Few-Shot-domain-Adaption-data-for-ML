"""
Filter and Verify LLM Responses
Script to process LLM feedback and create final filtered captions.

Author: CEIPP Crystallization Dataset
Date: 2025-12-18
"""

import os
import json
from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path

FILTER_OUTPUT = r"d:\user\CEIPP\Filter"


def load_json_file(file_path: str) -> Dict or List:
    """Load JSON file safely."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ Error: File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON in {file_path}: {e}")
        return None


def process_llm_response(llm_response: Dict, original_caption: Dict) -> Dict:
    """Process single LLM response and merge with original caption."""
    
    return {
        "image": original_caption["image"],
        "material_type": original_caption["material_type"],
        "material_name": original_caption["material_name"],
        "phase": original_caption["phase"],
        "original_caption": original_caption["initial_caption"],
        "llm_verification": {
            "confidence": llm_response.get("confidence", 0),
            "status": llm_response.get("status", "UNKNOWN"),
            "visual_observations": llm_response.get("visual_observations", ""),
            "caption_issues": llm_response.get("caption_issues", []),
            "notes": llm_response.get("notes", "")
        },
        "final_caption": llm_response.get("suggested_caption", original_caption["initial_caption"]),
        "revision_needed": llm_response.get("status") == "REVISION_NEEDED",
        "rejected": llm_response.get("status") == "REJECT",
        "processed_at": datetime.now().isoformat()
    }


def filter_captions(llm_responses: List[Dict], original_captions: List[Dict]) -> Tuple[List[Dict], Dict]:
    """Filter captions based on LLM feedback."""
    
    # Create mapping of image_id to original caption
    captions_map = {cap["image"]: cap for cap in original_captions}
    
    filtered = {
        "approved": [],
        "revision_needed": [],
        "rejected": [],
        "unprocessed": []
    }
    
    statistics = {
        "total_processed": 0,
        "approved": 0,
        "revision_needed": 0,
        "rejected": 0,
        "unprocessed": 0
    }
    
    # Process LLM responses
    processed_images = set()
    for llm_response in llm_responses:
        image_id = llm_response.get("image_id")
        processed_images.add(image_id)
        
        if image_id not in captions_map:
            print(f"⚠ Warning: LLM response for unknown image: {image_id}")
            continue
        
        original_caption = captions_map[image_id]
        merged = process_llm_response(llm_response, original_caption)
        
        status = llm_response.get("status", "UNKNOWN")
        if status == "APPROVE":
            filtered["approved"].append(merged)
            statistics["approved"] += 1
        elif status == "REVISION_NEEDED":
            filtered["revision_needed"].append(merged)
            statistics["revision_needed"] += 1
        elif status == "REJECT":
            filtered["rejected"].append(merged)
            statistics["rejected"] += 1
        
        statistics["total_processed"] += 1
    
    # Mark unprocessed captions
    for image_id, original_caption in captions_map.items():
        if image_id not in processed_images:
            merged = {
                "image": original_caption["image"],
                "material_type": original_caption["material_type"],
                "material_name": original_caption["material_name"],
                "phase": original_caption["phase"],
                "original_caption": original_caption["initial_caption"],
                "llm_verification": None,
                "final_caption": original_caption["initial_caption"],
                "revision_needed": False,
                "rejected": False,
                "processed_at": datetime.now().isoformat(),
                "status": "UNPROCESSED"
            }
            filtered["unprocessed"].append(merged)
            statistics["unprocessed"] += 1
    
    return filtered, statistics


def save_filtered_results(filtered: Dict, statistics: Dict) -> None:
    """Save filtered results and statistics."""
    
    # Create output directory
    os.makedirs(FILTER_OUTPUT, exist_ok=True)
    
    # Save approved captions
    if filtered["approved"]:
        approved_file = os.path.join(FILTER_OUTPUT, "annotated_captions", "approved_captions.json")
        os.makedirs(os.path.dirname(approved_file), exist_ok=True)
        with open(approved_file, 'w', encoding='utf-8') as f:
            json.dump(filtered["approved"], f, indent=2, ensure_ascii=False)
        print(f"✓ Saved: {approved_file} ({len(filtered['approved'])} captions)")
    
    # Save captions needing revision
    if filtered["revision_needed"]:
        revision_file = os.path.join(FILTER_OUTPUT, "annotated_captions", "revision_needed_captions.json")
        os.makedirs(os.path.dirname(revision_file), exist_ok=True)
        with open(revision_file, 'w', encoding='utf-8') as f:
            json.dump(filtered["revision_needed"], f, indent=2, ensure_ascii=False)
        print(f"✓ Saved: {revision_file} ({len(filtered['revision_needed'])} captions)")
    
    # Save rejected captions
    if filtered["rejected"]:
        rejected_file = os.path.join(FILTER_OUTPUT, "annotated_captions", "rejected_captions.json")
        os.makedirs(os.path.dirname(rejected_file), exist_ok=True)
        with open(rejected_file, 'w', encoding='utf-8') as f:
            json.dump(filtered["rejected"], f, indent=2, ensure_ascii=False)
        print(f"✓ Saved: {rejected_file} ({len(filtered['rejected'])} captions)")
    
    # Save unprocessed captions
    if filtered["unprocessed"]:
        unprocessed_file = os.path.join(FILTER_OUTPUT, "annotated_captions", "unprocessed_captions.json")
        os.makedirs(os.path.dirname(unprocessed_file), exist_ok=True)
        with open(unprocessed_file, 'w', encoding='utf-8') as f:
            json.dump(filtered["unprocessed"], f, indent=2, ensure_ascii=False)
        print(f"✓ Saved: {unprocessed_file} ({len(filtered['unprocessed'])} captions)")
    
    # Save comprehensive statistics
    stats_file = os.path.join(FILTER_OUTPUT, "filtering_statistics.json")
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump({
            "statistics": statistics,
            "timestamp": datetime.now().isoformat(),
            "breakdown": {
                "approved_count": len(filtered["approved"]),
                "revision_count": len(filtered["revision_needed"]),
                "rejected_count": len(filtered["rejected"]),
                "unprocessed_count": len(filtered["unprocessed"])
            }
        }, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved: {stats_file}")
    
    # Save comprehensive report
    report_file = os.path.join(FILTER_OUTPUT, "filtering_report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("LLM VERIFICATION FILTERING REPORT\n")
        f.write("=" * 70 + "\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write("SUMMARY\n")
        f.write("-" * 70 + "\n")
        f.write(f"Total Captions Processed:    {statistics['total_processed']:4}\n")
        f.write(f"Approved (Ready for Use):    {statistics['approved']:4}\n")
        f.write(f"Revision Needed:             {statistics['revision_needed']:4}\n")
        f.write(f"Rejected (Phase Mismatch):   {statistics['rejected']:4}\n")
        f.write(f"Unprocessed:                 {statistics['unprocessed']:4}\n")
        f.write("\n")
        
        if statistics['total_processed'] > 0:
            approval_rate = (statistics['approved'] / statistics['total_processed']) * 100
            f.write(f"Approval Rate: {approval_rate:.1f}%\n\n")
        
        f.write("NEXT STEPS\n")
        f.write("-" * 70 + "\n")
        if statistics['revision_needed'] > 0:
            f.write(f"1. Review {statistics['revision_needed']} captions in revision_needed_captions.json\n")
            f.write("2. Apply suggested revisions\n")
            f.write("3. Re-verify with LLM if major changes made\n\n")
        if statistics['rejected'] > 0:
            f.write(f"1. Review {statistics['rejected']} captions in rejected_captions.json\n")
            f.write("2. Manually re-classify images if needed\n")
            f.write("3. Investigate phase classification accuracy\n\n")
        f.write(f"Ready for Training Use: {statistics['approved']} approved captions\n")
    
    print(f"✓ Saved: {report_file}")


def create_llm_response_template() -> None:
    """Create template file for LLM responses."""
    
    template_file = os.path.join(FILTER_OUTPUT, "llm_verification_logs", "RESPONSE_TEMPLATE.json")
    os.makedirs(os.path.dirname(template_file), exist_ok=True)
    
    template = {
        "responses": [
            {
                "image_id": "1.jpg",
                "phase": "unsaturated",
                "confidence": 95,
                "status": "APPROVE",
                "visual_observations": "Clear, translucent solution with no visible crystals. High concentration evident from opacity.",
                "caption_issues": [],
                "suggested_caption": "Image showing unsaturated Physical Sugar (Dense Batch) solution at point A. High concentration, no visible crystal nucleation. System ready for de-supersaturation process.",
                "notes": "Clear match to unsaturated phase definition."
            },
            {
                "image_id": "101.jpg",
                "phase": "labile",
                "confidence": 85,
                "status": "REVISION_NEEDED",
                "visual_observations": "Initial crystal formation visible, but caption doesn't mention crystal size relative to labile phase.",
                "caption_issues": ["Missing crystal size descriptor", "Could be more specific about nucleation stage"],
                "suggested_caption": "Image showing labile phase around point B in Physical Sugar (Dense Batch) system. Small crystals beginning to nucleate. Transition from unsaturated to crystallization phase with initial seed formation.",
                "notes": "Generally correct but needs detail enhancement."
            },
            {
                "image_id": "201.jpg",
                "phase": "intermediate",
                "confidence": 45,
                "status": "REJECT",
                "visual_observations": "This appears to be metastable phase with very high crystal density, not intermediate phase.",
                "caption_issues": ["Phase misclassification", "Crystal density too high for intermediate"],
                "suggested_caption": "Should be reclassified to metastable phase.",
                "notes": "Recommend moving to metastable category."
            }
        ]
    }
    
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    print(f"✓ Created: {template_file}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("LLM Response Filtering & Analysis")
    print("=" * 70)
    
    # Check for required files
    llm_responses_file = os.path.join(FILTER_OUTPUT, "llm_verification_logs", "llm_responses.json")
    captions_file = os.path.join(FILTER_OUTPUT, "all_initial_captions.json")
    
    print(f"\nLooking for LLM responses...")
    if not os.path.exists(llm_responses_file):
        print(f"✗ LLM responses file not found: {llm_responses_file}")
        print("\nTo use this script:")
        print("1. Create LLM verification batch with prepare_llm_batch.py")
        print("2. Send images to multi-modal LLM for verification")
        print("3. Save LLM responses to: {llm_responses_file}")
        print("4. Run this script again")
        print("\nResponse format template saved at:")
        create_llm_response_template()
        return
    
    if not os.path.exists(captions_file):
        print(f"✗ Original captions file not found: {captions_file}")
        print("  Please run generate_initial_captions.py first")
        return
    
    # Load data
    print("Loading data...")
    llm_responses_data = load_json_file(llm_responses_file)
    original_captions = load_json_file(captions_file)
    
    if not llm_responses_data or not original_captions:
        print("✗ Failed to load required data")
        return
    
    # Handle different response formats
    if isinstance(llm_responses_data, dict) and "responses" in llm_responses_data:
        llm_responses = llm_responses_data["responses"]
    else:
        llm_responses = llm_responses_data if isinstance(llm_responses_data, list) else []
    
    print(f"✓ Loaded {len(original_captions)} original captions")
    print(f"✓ Loaded {len(llm_responses)} LLM responses\n")
    
    # Filter captions
    print("Processing and filtering captions...")
    filtered, statistics = filter_captions(llm_responses, original_captions)
    
    # Save results
    print("\nSaving filtered results...")
    save_filtered_results(filtered, statistics)
    
    # Print summary
    print("\n" + "=" * 70)
    print("FILTERING COMPLETE - SUMMARY")
    print("=" * 70)
    print(f"Total Processed:      {statistics['total_processed']}")
    print(f"Approved:             {statistics['approved']}")
    print(f"Revision Needed:      {statistics['revision_needed']}")
    print(f"Rejected:             {statistics['rejected']}")
    print(f"Unprocessed:          {statistics['unprocessed']}")
    if statistics['total_processed'] > 0:
        approval_rate = (statistics['approved'] / statistics['total_processed']) * 100
        print(f"Approval Rate:        {approval_rate:.1f}%")
    print("=" * 70)
    print("\nOutput Files:")
    print("- approved_captions.json (ready for training)")
    print("- revision_needed_captions.json (requires edits)")
    print("- rejected_captions.json (phase verification needed)")
    print("- unprocessed_captions.json (awaiting LLM verification)")
    print("- filtering_statistics.json (detailed stats)")
    print("- filtering_report.txt (summary report)")
    print("=" * 70)


if __name__ == "__main__":
    main()
