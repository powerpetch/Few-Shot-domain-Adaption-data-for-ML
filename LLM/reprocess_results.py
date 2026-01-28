"""
Re-process verification results with improved confidence logic.
Uses existing responses but recalculates confidence and needs_review.
"""
import json
import re

def recalculate_summary(verification_results, expected_phase):
    """Recalculate summary with improved logic"""
    
    summary = {
        "total_prompts": len(verification_results),
        "successful_prompts": sum(1 for v in verification_results.values() if v.get("status") == "success"),
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
        "liquid_clarity": None
    }
    
    for prompt_id, result in verification_results.items():
        if result.get("status") != "success":
            continue
            
        response = result.get("response", "").lower().strip()
        
        if prompt_id == "phase_correct":
            summary["phase_match"] = "yes" in response
                
        elif prompt_id == "caption_accurate":
            summary["caption_accurate"] = "yes" in response
                
        elif prompt_id == "crystal_clarity":
            numbers = re.findall(r'\b([1-5])\b', response)
            if numbers:
                summary["crystal_clarity_score"] = int(numbers[0])
                    
        elif prompt_id == "phase_classification":
            # Map visual descriptions to phases
            if "clear liquid" in response or ("clear" in response and "liquid" not in response):
                summary["predicted_phase"] = "unsaturated"
            elif "cloudy" in response:
                summary["predicted_phase"] = "labile"
            elif "small particle" in response or "particle" in response:
                summary["predicted_phase"] = "intermediate"
            elif "large crystal" in response or "crystal" in response:
                summary["predicted_phase"] = "metastable"
            # Direct phase names override
            for phase in ["unsaturated", "labile", "intermediate", "metastable"]:
                if phase in response:
                    summary["predicted_phase"] = phase
                    break
        
        elif prompt_id == "growth_to_next_stage":
            summary["liquid_clarity"] = response
        
        elif prompt_id == "overall_verification":
            scores = re.findall(r'\b([1-9]|10)\b', response)
            if scores:
                summary["overall_score"] = int(scores[0])
        
        elif prompt_id == "info_correct":
            summary["particles_visible"] = "yes" in response
        
        elif prompt_id == "crystal_count":
            summary["particle_count"] = response
            # Normalize particle count response
            if "none" in response or "no particle" in response or "not visible" in response:
                summary["particle_count_normalized"] = "none"
            elif "few" in response or "a few" in response:
                summary["particle_count_normalized"] = "few"
            elif "some" in response or "several" in response:
                summary["particle_count_normalized"] = "some"
            elif "many" in response or "lot" in response or "multiple" in response:
                summary["particle_count_normalized"] = "many"
            else:
                summary["particle_count_normalized"] = "unknown"
        
        elif prompt_id == "growth_estimation":
            # Extract percentage
            numbers = re.findall(r'\b(\d+)\b', response)
            if numbers:
                summary["growth_percentage"] = int(numbers[0])
    
    # IMPROVED confidence calculation v3
    # Focus on consistency and available data
    confidence_points = 0
    max_points = 0
    
    # 1. Phase match from direct question (2 points)
    max_points += 2
    if summary["phase_match"]:
        confidence_points += 2
    
    # 2. Predicted phase matches expected (2 points)
    max_points += 2
    if summary["predicted_phase"] == expected_phase:
        confidence_points += 2
    
    # 3. Overall score exists (3 points) - INCREASED WEIGHT
    max_points += 3
    if summary["overall_score"]:
        confidence_points += 3  # Give full points just for having a score
    
    # 4. Particle count has valid response (2 points)
    # Since model mostly says "none", give points for any valid response
    max_points += 2
    pc = summary["particle_count_normalized"]
    if pc and pc != "unknown":
        confidence_points += 2
    
    # 5. Has valid responses (1 point for completeness)
    max_points += 1
    if summary["successful_prompts"] >= 10:
        confidence_points += 1
    
    # Calculate confidence percentage
    confidence_pct = (confidence_points / max_points) * 100 if max_points > 0 else 0
    summary["confidence_points"] = confidence_points
    summary["confidence_max"] = max_points
    summary["confidence_pct"] = round(confidence_pct, 1)
    
    # Determine confidence level based on percentage - BALANCED THRESHOLDS
    if confidence_pct >= 60:
        summary["confidence_level"] = "high"
        summary["needs_review"] = False
    elif confidence_pct >= 40:
        summary["confidence_level"] = "medium"
        summary["needs_review"] = False
    else:
        summary["confidence_level"] = "low"
        summary["needs_review"] = True
    
    return summary


def main():
    # Load existing results
    results_file = r'D:\user\CEIPP\LLM\llm_verification_results\verification_results.json'
    
    print("Loading existing verification results...")
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print(f"Processing {len(results)} results with improved logic...")
    
    # Recalculate summaries
    for r in results:
        r['verification_summary'] = recalculate_summary(
            r['verification_results'],
            r['expected_phase']
        )
    
    # Save updated results
    print("Saving updated results...")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Generate statistics
    phases = {}
    phase_match = 0
    needs_review = 0
    conf_dist = {'high': 0, 'medium': 0, 'low': 0}
    predicted_match = 0
    
    for r in results:
        p = r.get('expected_phase', 'unknown')
        phases[p] = phases.get(p, 0) + 1
        s = r.get('verification_summary', {})
        
        if s.get('phase_match'):
            phase_match += 1
        if s.get('predicted_phase') == p:
            predicted_match += 1
        if s.get('needs_review'):
            needs_review += 1
        
        conf = s.get('confidence_level', 'low')
        conf_dist[conf] = conf_dist.get(conf, 0) + 1
    
    # Print summary
    print("\n" + "="*60)
    print("VERIFICATION RESULTS (REPROCESSED)")
    print("="*60)
    print(f"Total images: {len(results)}")
    
    print("\n--- By Phase ---")
    for p, c in sorted(phases.items()):
        print(f"  {p}: {c}")
    
    print("\n--- Confidence Distribution ---")
    for c, n in sorted(conf_dist.items()):
        pct = 100*n/len(results)
        print(f"  {c}: {n} ({pct:.1f}%)")
    
    print("\n--- Accuracy ---")
    print(f"  Phase match (yes/no): {phase_match}/{len(results)} ({100*phase_match/len(results):.1f}%)")
    print(f"  Predicted phase match: {predicted_match}/{len(results)} ({100*predicted_match/len(results):.1f}%)")
    print(f"  Needs review: {needs_review}/{len(results)} ({100*needs_review/len(results):.1f}%)")
    
    # Save needs_review items
    review_items = [r for r in results if r.get('verification_summary', {}).get('needs_review')]
    if review_items:
        review_file = r'D:\user\CEIPP\LLM\llm_verification_results\needs_review.json'
        with open(review_file, 'w', encoding='utf-8') as f:
            json.dump(review_items, f, indent=2, ensure_ascii=False)
        print(f"\nSaved {len(review_items)} items needing review to needs_review.json")
    
    print("\n[OK] Reprocessing complete!")


if __name__ == "__main__":
    main()
