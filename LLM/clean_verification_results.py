"""
Clean LLM Verification Results - Remove Invalid/Noise Responses

This script cleans the verification results by:
1. Validating response types (score must be a number, yes_no must be yes/no, etc.)
2. Marking invalid responses as 'invalid' status
3. Recalculating confidence scores excluding invalid responses
4. Regenerating needs_review.json and statistics

Author: Copilot
Date: 2026-01-25
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple


# Paths
LLM_PATH = Path(__file__).parent
RESULTS_FILE = LLM_PATH / "llm_verification_results" / "verification_results.json"
NEEDS_REVIEW_FILE = LLM_PATH / "llm_verification_results" / "needs_review.json"
STATISTICS_FILE = LLM_PATH / "llm_verification_results" / "verification_statistics.json"
BACKUP_FOLDER = LLM_PATH / "llm_verification_results" / "backups"


def validate_response(response: str, response_type: str, prompt_id: str) -> Tuple[bool, Any]:
    """
    Validate a response based on its expected type.
    
    Args:
        response: The raw response string
        response_type: Expected type ('score', 'yes_no', 'classification', 'description')
        prompt_id: The prompt identifier for context
    
    Returns:
        Tuple of (is_valid, cleaned_value)
    """
    if response is None:
        return False, None
    
    response = response.strip().lower()
    
    if response_type == "yes_no":
        # Must contain 'yes' or 'no'
        if "yes" in response:
            return True, "yes"
        elif "no" in response:
            return True, "no"
        return False, None
    
    elif response_type == "score":
        # Different score ranges based on prompt
        if prompt_id == "crystal_clarity" or prompt_id == "image_quality":
            # Should be 1-5
            numbers = re.findall(r'\b([1-5])\b', response)
            if numbers:
                return True, int(numbers[0])
            # Try to find any single digit
            digits = re.findall(r'\b(\d)\b', response)
            if digits and 1 <= int(digits[0]) <= 5:
                return True, int(digits[0])
            return False, None
        
        elif prompt_id == "overall_verification":
            # Should be 1-10
            numbers = re.findall(r'\b([1-9]|10)\b', response)
            if numbers:
                return True, int(numbers[0])
            return False, None
        
        elif prompt_id == "growth_estimation":
            # Should be 0-100
            numbers = re.findall(r'\b(\d{1,3})\b', response)
            if numbers:
                num = int(numbers[0])
                if 0 <= num <= 100:
                    return True, num
            return False, None
        
        # Generic score validation
        numbers = re.findall(r'\b(\d+)\b', response)
        if numbers:
            return True, int(numbers[0])
        return False, None
    
    elif response_type == "classification":
        if prompt_id == "phase_classification":
            valid_responses = ["clear liquid", "cloudy liquid", "small particles", "large crystals",
                              "clear", "cloudy", "particles", "crystals"]
            for valid in valid_responses:
                if valid in response:
                    return True, response
            # Also check for phase names directly
            for phase in ["unsaturated", "labile", "intermediate", "metastable"]:
                if phase in response:
                    return True, response
            return False, None
        
        elif prompt_id == "growth_to_next_stage":
            if "clear" in response or "cloudy" in response:
                return True, "clear" if "clear" in response else "cloudy"
            return False, None
        
        elif prompt_id == "material_type":
            if "photo" in response or "photograph" in response:
                return True, "photo"
            elif "generated" in response or "computer" in response or "simulated" in response:
                return True, "generated"
            return False, None
        
        elif prompt_id == "crystal_count":
            valid_counts = ["none", "few", "some", "many"]
            for vc in valid_counts:
                if vc in response:
                    return True, vc
            # Check for zero
            if "0" in response or "no " in response or "not visible" in response:
                return True, "none"
            return False, None
        
        # Generic classification - assume valid if not empty
        return bool(response), response
    
    elif response_type == "description":
        # Descriptions are generally always valid if not empty
        # But check for obvious garbage
        garbage_patterns = [
            r"^i (don't|have no) (know|idea)",
            r"^if you can't",
            r"^what do you",
            r"^i can't",
            r"^\?+$",
        ]
        for pattern in garbage_patterns:
            if re.match(pattern, response):
                return False, None
        return bool(response), response
    
    return bool(response), response


def clean_verification_result(result: Dict) -> Dict:
    """
    Clean a single verification result entry.
    
    Args:
        result: A verification result dictionary
    
    Returns:
        Cleaned result with validation status
    """
    verification_results = result.get("verification_results", {})
    
    valid_count = 0
    invalid_count = 0
    
    for prompt_id, data in verification_results.items():
        response = data.get("response", "")
        response_type = data.get("response_type", "")
        
        is_valid, cleaned_value = validate_response(response, response_type, prompt_id)
        
        if is_valid:
            data["validation_status"] = "valid"
            data["cleaned_value"] = cleaned_value
            valid_count += 1
        else:
            data["validation_status"] = "invalid"
            data["cleaned_value"] = None
            invalid_count += 1
    
    # Update verification results
    result["verification_results"] = verification_results
    
    # Recalculate summary with only valid responses
    result["verification_summary"] = recalculate_summary_clean(verification_results, result.get("expected_phase", ""))
    result["validation_stats"] = {
        "valid_responses": valid_count,
        "invalid_responses": invalid_count,
        "validation_rate": round(valid_count / (valid_count + invalid_count) * 100, 1) if (valid_count + invalid_count) > 0 else 0
    }
    
    return result


def recalculate_summary_clean(verification_results: Dict, expected_phase: str) -> Dict:
    """
    Recalculate summary using only valid responses.
    """
    summary = {
        "total_prompts": len(verification_results),
        "successful_prompts": 0,
        "valid_responses": 0,
        "phase_match": None,
        "caption_accurate": None,
        "crystal_clarity_score": None,
        "predicted_phase": None,
        "overall_score": None,
        "needs_review": False,
        "confidence_level": "unknown",
        "particles_visible": None,
        "particle_count": None,
        "particle_count_normalized": None,
        "liquid_clarity": None,
        "growth_percentage": None
    }
    
    # Only process valid responses
    for prompt_id, result in verification_results.items():
        if result.get("status") != "success":
            continue
        
        summary["successful_prompts"] += 1
        
        # Skip invalid responses
        if result.get("validation_status") != "valid":
            continue
        
        summary["valid_responses"] += 1
        cleaned = result.get("cleaned_value")
        response = result.get("response", "").lower().strip()
        
        if prompt_id == "phase_correct":
            summary["phase_match"] = cleaned == "yes"
        
        elif prompt_id == "caption_accurate":
            summary["caption_accurate"] = cleaned == "yes"
        
        elif prompt_id == "crystal_clarity":
            if isinstance(cleaned, int):
                summary["crystal_clarity_score"] = cleaned
        
        elif prompt_id == "phase_classification":
            # Map visual descriptions to phases
            if cleaned:
                if "clear liquid" in cleaned or ("clear" in cleaned and "liquid" not in cleaned):
                    summary["predicted_phase"] = "unsaturated"
                elif "cloudy" in cleaned:
                    summary["predicted_phase"] = "labile"
                elif "small particle" in cleaned or "particle" in cleaned:
                    summary["predicted_phase"] = "intermediate"
                elif "large crystal" in cleaned or "crystal" in cleaned:
                    summary["predicted_phase"] = "metastable"
                # Direct phase names override
                for phase in ["unsaturated", "labile", "intermediate", "metastable"]:
                    if phase in cleaned:
                        summary["predicted_phase"] = phase
                        break
        
        elif prompt_id == "growth_to_next_stage":
            summary["liquid_clarity"] = cleaned
        
        elif prompt_id == "overall_verification":
            if isinstance(cleaned, int):
                summary["overall_score"] = cleaned
        
        elif prompt_id == "info_correct":
            summary["particles_visible"] = cleaned == "yes"
        
        elif prompt_id == "crystal_count":
            summary["particle_count"] = response
            summary["particle_count_normalized"] = cleaned
        
        elif prompt_id == "growth_estimation":
            if isinstance(cleaned, int):
                summary["growth_percentage"] = cleaned
    
    # Calculate confidence based on VALID responses only
    confidence_points = 0
    max_points = 0
    
    # 1. Phase match from direct question (2 points)
    if summary["phase_match"] is not None:
        max_points += 2
        if summary["phase_match"]:
            confidence_points += 2
    
    # 2. Predicted phase matches expected (2 points)
    if summary["predicted_phase"] is not None:
        max_points += 2
        if summary["predicted_phase"] == expected_phase:
            confidence_points += 2
    
    # 3. Overall score exists and is valid (3 points)
    if summary["overall_score"] is not None:
        max_points += 3
        if summary["overall_score"] >= 5:
            confidence_points += 3
        elif summary["overall_score"] >= 3:
            confidence_points += 2
        else:
            confidence_points += 1
    
    # 4. Crystal clarity score (2 points)
    if summary["crystal_clarity_score"] is not None:
        max_points += 2
        if summary["crystal_clarity_score"] >= 3:
            confidence_points += 2
        elif summary["crystal_clarity_score"] >= 2:
            confidence_points += 1
    
    # 5. Particle count has valid response (1 point)
    if summary["particle_count_normalized"] is not None:
        max_points += 1
        confidence_points += 1
    
    # 6. Valid response ratio bonus (1 point if >70% valid)
    max_points += 1
    valid_ratio = summary["valid_responses"] / summary["successful_prompts"] if summary["successful_prompts"] > 0 else 0
    if valid_ratio >= 0.7:
        confidence_points += 1
    
    # Calculate confidence percentage
    confidence_pct = (confidence_points / max_points * 100) if max_points > 0 else 0
    summary["confidence_points"] = confidence_points
    summary["confidence_max"] = max_points
    summary["confidence_pct"] = round(confidence_pct, 1)
    
    # Determine confidence level - stricter thresholds
    if confidence_pct >= 60 and valid_ratio >= 0.6:
        summary["confidence_level"] = "high"
        summary["needs_review"] = False
    elif confidence_pct >= 40 and valid_ratio >= 0.5:
        summary["confidence_level"] = "medium"
        summary["needs_review"] = False
    else:
        summary["confidence_level"] = "low"
        summary["needs_review"] = True
    
    return summary


def generate_statistics(results: list) -> Dict:
    """Generate comprehensive statistics from cleaned results."""
    stats = {
        "total_processed": len(results),
        "successful": 0,
        "errors": 0,
        "by_phase": {},
        "phase_match_rate": 0,
        "caption_accuracy_rate": 0,
        "needs_review_count": 0,
        "validation_summary": {
            "total_valid_responses": 0,
            "total_invalid_responses": 0,
            "avg_validation_rate": 0
        },
        "confidence_distribution": {
            "high": 0,
            "medium": 0,
            "low": 0
        },
        "invalid_response_types": {},
        "cleaned_timestamp": datetime.now().isoformat()
    }
    
    phase_match_count = 0
    caption_accurate_count = 0
    total_valid = 0
    total_invalid = 0
    
    for r in results:
        summary = r.get("verification_summary", {})
        phase = r.get("expected_phase", "unknown")
        validation = r.get("validation_stats", {})
        
        # Count by phase
        if phase not in stats["by_phase"]:
            stats["by_phase"][phase] = {"total": 0, "phase_match": 0, "caption_accurate": 0, "needs_review": 0}
        
        stats["by_phase"][phase]["total"] += 1
        
        if summary.get("phase_match"):
            phase_match_count += 1
            stats["by_phase"][phase]["phase_match"] += 1
        
        if summary.get("caption_accurate"):
            caption_accurate_count += 1
            stats["by_phase"][phase]["caption_accurate"] += 1
        
        if summary.get("needs_review"):
            stats["needs_review_count"] += 1
            stats["by_phase"][phase]["needs_review"] += 1
        
        # Confidence distribution
        conf = summary.get("confidence_level", "low")
        stats["confidence_distribution"][conf] = stats["confidence_distribution"].get(conf, 0) + 1
        
        # Validation stats
        total_valid += validation.get("valid_responses", 0)
        total_invalid += validation.get("invalid_responses", 0)
        
        # Track invalid response types
        for prompt_id, data in r.get("verification_results", {}).items():
            if data.get("validation_status") == "invalid":
                response_type = data.get("response_type", "unknown")
                key = f"{prompt_id}_{response_type}"
                stats["invalid_response_types"][key] = stats["invalid_response_types"].get(key, 0) + 1
    
    # Calculate rates
    stats["phase_match_rate"] = round(phase_match_count / len(results), 4) if results else 0
    stats["caption_accuracy_rate"] = round(caption_accurate_count / len(results), 4) if results else 0
    
    # Validation summary
    total_responses = total_valid + total_invalid
    stats["validation_summary"]["total_valid_responses"] = total_valid
    stats["validation_summary"]["total_invalid_responses"] = total_invalid
    stats["validation_summary"]["avg_validation_rate"] = round(total_valid / total_responses * 100, 1) if total_responses > 0 else 0
    
    stats["successful"] = len(results) - stats["needs_review_count"]
    
    return stats


def main():
    """Main cleaning function."""
    print("=" * 70)
    print("LLM Verification Results Cleaner")
    print("=" * 70)
    
    # Check if files exist
    if not RESULTS_FILE.exists():
        print(f"[ERROR] Results file not found: {RESULTS_FILE}")
        return
    
    # Create backup
    BACKUP_FOLDER.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"\n[1/5] Loading verification results...")
    with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
        results = json.load(f)
    print(f"       Loaded {len(results)} results")
    
    # Backup original
    print(f"\n[2/5] Creating backup...")
    backup_file = BACKUP_FOLDER / f"verification_results_backup_{timestamp}.json"
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"       Backup saved to: {backup_file.name}")
    
    # Clean results
    print(f"\n[3/5] Cleaning and validating responses...")
    cleaned_results = []
    invalid_examples = []
    
    for i, result in enumerate(results):
        cleaned = clean_verification_result(result)
        cleaned_results.append(cleaned)
        
        # Collect examples of invalid responses (first 5)
        if len(invalid_examples) < 5:
            for prompt_id, data in cleaned.get("verification_results", {}).items():
                if data.get("validation_status") == "invalid":
                    invalid_examples.append({
                        "image": cleaned.get("image_name"),
                        "prompt_id": prompt_id,
                        "prompt": data.get("prompt", "")[:50] + "...",
                        "response": data.get("response", ""),
                        "response_type": data.get("response_type")
                    })
                    break
    
    # Show some invalid examples
    if invalid_examples:
        print("\n       Sample invalid responses found:")
        for ex in invalid_examples[:5]:
            print(f"       - [{ex['prompt_id']}] Expected {ex['response_type']}, got: '{ex['response']}'")
    
    # Generate statistics
    print(f"\n[4/5] Generating statistics...")
    stats = generate_statistics(cleaned_results)
    
    # Filter needs_review
    needs_review = [r for r in cleaned_results if r.get("verification_summary", {}).get("needs_review")]
    
    # Save cleaned results
    print(f"\n[5/5] Saving cleaned files...")
    
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(cleaned_results, f, indent=2, ensure_ascii=False)
    print(f"       Updated: verification_results.json")
    
    with open(NEEDS_REVIEW_FILE, 'w', encoding='utf-8') as f:
        json.dump(needs_review, f, indent=2, ensure_ascii=False)
    print(f"       Updated: needs_review.json ({len(needs_review)} items)")
    
    with open(STATISTICS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"       Updated: verification_statistics.json")
    
    # Print summary
    print("\n" + "=" * 70)
    print("CLEANING SUMMARY")
    print("=" * 70)
    print(f"Total images:         {stats['total_processed']}")
    print(f"Valid responses:      {stats['validation_summary']['total_valid_responses']}")
    print(f"Invalid responses:    {stats['validation_summary']['total_invalid_responses']}")
    print(f"Validation rate:      {stats['validation_summary']['avg_validation_rate']}%")
    
    print(f"\nConfidence Distribution:")
    for level, count in stats['confidence_distribution'].items():
        pct = round(count / stats['total_processed'] * 100, 1) if stats['total_processed'] > 0 else 0
        print(f"  {level:8s}: {count:5d} ({pct}%)")
    
    print(f"\nNeeds Review:         {stats['needs_review_count']} images")
    print(f"Phase Match Rate:     {stats['phase_match_rate']*100:.1f}%")
    
    if stats['invalid_response_types']:
        print(f"\nMost Common Invalid Response Types:")
        sorted_invalid = sorted(stats['invalid_response_types'].items(), key=lambda x: -x[1])[:5]
        for key, count in sorted_invalid:
            print(f"  {key}: {count} occurrences")
    
    print("\n" + "=" * 70)
    print("Cleaning complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
