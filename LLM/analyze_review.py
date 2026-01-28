import json

results = json.load(open(r'D:\user\CEIPP\LLM\llm_verification_results\verification_results.json'))

# Check what makes low confidence
low_conf = [r for r in results if r.get('verification_summary', {}).get('confidence_level') == 'low']
print(f'Low confidence items: {len(low_conf)}')

# Sample analysis
print('\n=== Sample of low confidence items ===')
for r in low_conf[:3]:
    s = r['verification_summary']
    print(f"Image: {r['image_name']}")
    print(f"  Phase match: {s.get('phase_match')}")
    print(f"  Caption accurate: {s.get('caption_accurate')}")
    print(f"  Crystal clarity: {s.get('crystal_clarity_score')}")
    print(f"  Overall score: {s.get('overall_score')}")
    print()

# Count factor distribution
phase_true = sum(1 for r in low_conf if r['verification_summary'].get('phase_match') == True)
caption_true = sum(1 for r in low_conf if r['verification_summary'].get('caption_accurate') == True)
overall_7plus = sum(1 for r in low_conf if (r['verification_summary'].get('overall_score') or 0) >= 7)
clarity_3plus = sum(1 for r in low_conf if (r['verification_summary'].get('crystal_clarity_score') or 0) >= 3)

print(f'=== In low confidence group ({len(low_conf)}) ===')
print(f'  Phase match True: {phase_true}')
print(f'  Caption accurate True: {caption_true}')
print(f'  Overall score >= 7: {overall_7plus}')
print(f'  Crystal clarity >= 3: {clarity_3plus}')

# Check actual responses
print('\n=== Sample responses causing issues ===')
for r in low_conf[:2]:
    vr = r['verification_results']
    print(f"\nImage: {r['image_name']}")
    print(f"  phase_correct response: {vr.get('phase_correct', {}).get('response')}")
    print(f"  caption_accurate response: {vr.get('caption_accurate', {}).get('response')}")
    print(f"  crystal_clarity response: {vr.get('crystal_clarity', {}).get('response')}")
    print(f"  overall_verification response: {vr.get('overall_verification', {}).get('response')}")
