import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

BASE_PATH = Path(__file__).parent.parent
DATASET_ROOT = BASE_PATH / "_21p1_pjirayu_Seed-Crystallization-Dataset" / "balanced_crystallization"
FILTER_OUTPUT = BASE_PATH / "Filter"

VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}


# PROCESS STAGES MAPPING (10 Stages from industrial process)

# Based on the batch pan operation stages:
# Charging -> Concentration -> Seeding -> Graining -> Boiling -> Boiling_Hold -> Boiling_End -> Tightening -> Discharge -> Cleaning

PROCESS_STAGES = {
    "charging": {"order": 1, "phase": "unsaturated", "description": "Initial syrup feeding into vacuum pan"},
    "concentration": {"order": 2, "phase": "unsaturated", "description": "Evaporation to reach supersaturation"},
    "seeding": {"order": 3, "phase": "labile", "description": "Introduction of seed crystals/nucleation"},
    "graining": {"order": 4, "phase": "labile", "description": "Initial grain establishment"},
    "boiling": {"order": 5, "phase": "intermediate", "description": "Active crystal growth phase"},
    "boiling_hold": {"order": 6, "phase": "intermediate", "description": "Controlled growth maintenance"},
    "boiling_end": {"order": 7, "phase": "intermediate", "description": "Final crystal growth completion"},
    "tightening": {"order": 8, "phase": "metastable", "description": "Density increase and final solidification"},
    "discharge": {"order": 9, "phase": "metastable", "description": "Batch completion and crystal extraction"},
    "cleaning": {"order": 10, "phase": "complete", "description": "Pan cleaning and preparation for next batch"}
}


# CRYSTAL GROWTH PERCENTAGE MODEL

# Growth percentage estimation based on:
# - Crystallization phase (from solubility diagram)
# - Typical industrial batch crystallization curves
# - Visual characteristics of crystal development

@dataclass
class GrowthStageInfo:
    """Information about crystal growth at each stage"""
    phase: str
    growth_percentage_range: Tuple[int, int]  # (min%, max%)
    cumulative_growth: int  # average cumulative growth %
    growth_rate_description: str
    next_step: str
    expected_visual_changes: List[str]
    process_stage_mapping: List[str]

GROWTH_STAGES = {
    "unsaturated": GrowthStageInfo(
        phase="unsaturated",
        growth_percentage_range=(0, 5),
        cumulative_growth=0,
        growth_rate_description="No crystal growth - solution preparation phase",
        next_step="Seeding (Labile phase)",
        expected_visual_changes=[
            "Clear homogeneous solution",
            "Increasing concentration/viscosity",
            "No visible crystals or nuclei"
        ],
        process_stage_mapping=["charging", "concentration"]
    ),
    "labile": GrowthStageInfo(
        phase="labile",
        growth_percentage_range=(5, 20),
        cumulative_growth=15,
        growth_rate_description="Initial nucleation - rapid seed formation",
        next_step="Boiling (Intermediate phase)",
        expected_visual_changes=[
            "First appearance of crystal nuclei",
            "Tiny scattered bright specks",
            "Dark background with emerging points",
            "Rapid nucleation events"
        ],
        process_stage_mapping=["seeding", "graining"]
    ),
    "intermediate": GrowthStageInfo(
        phase="intermediate",
        growth_percentage_range=(20, 70),
        cumulative_growth=50,
        growth_rate_description="Active growth - main crystal development phase",
        next_step="Tightening (Metastable phase)",
        expected_visual_changes=[
            "Distinct crystal shapes forming",
            "Rectangular/prismatic structures visible",
            "Crystal size increasing",
            "Separation between individual crystals",
            "Clear geometric boundaries"
        ],
        process_stage_mapping=["boiling", "boiling_hold", "boiling_end"]
    ),
    "metastable": GrowthStageInfo(
        phase="metastable",
        growth_percentage_range=(70, 100),
        cumulative_growth=90,
        growth_rate_description="Final growth - crystal maturation and packing",
        next_step="Batch Complete (Discharge/Cleaning)",
        expected_visual_changes=[
            "Dense crystal packing",
            "Interlocking mosaic pattern",
            "Fully formed faceted crystals",
            "High density coverage",
            "Little to no background visible"
        ],
        process_stage_mapping=["tightening", "discharge"]
    )
}


# MATERIAL-SPECIFIC TEMPLATES (Enhanced with growth info)


MATERIALS = {
    "phy_sugar_db": "Physical Sugar (Dense Batch)",
    "phy_sugar_opr": "Physical Sugar (Operation)",
    "vir_polymer": "Virtual Polymer"
}

MATERIAL_SPECIFIC_TEMPLATES = {
    "phy_sugar_db": {
        "unsaturated": {
            "description": "Dense sugar solution below saturation - preparation phase",
            "template": (
                "Microscopic view of an unsaturated {material} solution during {process_stages}. "
                "Crystal growth progress: {growth_pct}%. "
                "The image displays a uniform, featureless amber background indicating a homogeneous liquid phase. "
                "No crystal structures are visible. Next milestone: {next_step}."
            ),
            "visual_markers": ["Homogeneous amber background", "Featureless liquid", "No particles", "Clear solution"]
        },
        "labile": {
            "description": "Initial seeding and nucleation phase",
            "template": (
                "Microscopic view of the labile phase in {material} ({process_stages}). "
                "Crystal growth progress: {growth_pct}%. "
                "The image shows initial nucleation with sparse, minute bright specks emerging on a dark field. "
                "These isolated points represent seed crystals forming. Next milestone: {next_step}."
            ),
            "visual_markers": ["Dark background", "Tiny scattered bright specks", "Initial nucleation", "Seed formation"]
        },
        "intermediate": {
            "description": "Active crystal growth phase",
            "template": (
                "Microscopic view of the intermediate crystallization phase in {material} during {process_stages}. "
                "Crystal growth progress: {growth_pct}%. "
                "Distinct rectangular and prismatic crystal shapes are clearly visible with varying sizes. "
                "Active growth is occurring with separation between structures. Next milestone: {next_step}."
            ),
            "visual_markers": ["Rectangular prisms", "Defined edges", "Separated crystals", "Geometric shapes", "Growing structures"]
        },
        "metastable": {
            "description": "Final crystal maturation phase",
            "template": (
                "Microscopic view of the metastable phase in {material} ({process_stages}). "
                "Crystal growth progress: {growth_pct}%. "
                "The frame is completely filled with a dense, interlocking mosaic of fully formed crystals. "
                "Large, faceted structures crowd against one another. Next milestone: {next_step}."
            ),
            "visual_markers": ["Interlocking mosaic", "Crowded field", "High density", "No background", "Fully formed crystals"]
        }
    },
    "phy_sugar_opr": {
        "unsaturated": {
            "description": "Operational sugar solution preparation",
            "template": (
                "Microscopic view of an unsaturated {material} fluid during {process_stages}. "
                "Crystal growth progress: {growth_pct}%. "
                "The image shows a smooth, light gradient background free of crystalline geometry. "
                "Only sparse spherical artifacts (bubbles) may be present. Next milestone: {next_step}."
            ),
            "visual_markers": ["Smooth light background", "Spherical bubbles", "No crystal angles", "Homogeneous liquid"]
        },
        "labile": {
            "description": "Operational seeding and nucleation",
            "template": (
                "Microscopic view of the labile phase in {material} ({process_stages}). "
                "Crystal growth progress: {growth_pct}%. "
                "Small, irregular dark aggregates and clumps scattered across the frame indicate nucleation onset. "
                "These distinct clusters show solid formation beginning. Next milestone: {next_step}."
            ),
            "visual_markers": ["Scattered dark clumps", "Irregular aggregates", "Wide spacing", "Initial solid formation"]
        },
        "intermediate": {
            "description": "Operational crystal growth",
            "template": (
                "Microscopic view of the intermediate crystallization phase in {material} during {process_stages}. "
                "Crystal growth progress: {growth_pct}%. "
                "Large, translucent cubic and rectangular prisms are visible floating in solution. "
                "Crystals exhibit sharp edges and distinct 3D volume. Next milestone: {next_step}."
            ),
            "visual_markers": ["Translucent cubes", "Rectangular prisms", "Sharp straight edges", "3D volume", "Crystal clarity"]
        },
        "metastable": {
            "description": "Operational completion phase",
            "template": (
                "Microscopic view of the metastable phase in {material} during {process_stages}. "
                "Crystal growth progress: {growth_pct}%. "
                "High-density accumulation of bright, opaque crystal structures fills the view. "
                "Crystals are heavily overlapped and packed, indicating batch completion. Next milestone: {next_step}."
            ),
            "visual_markers": ["Bright opaque crystals", "Dense packing", "Heavily overlapped", "Textured surface", "Full coverage"]
        }
    },
    "vir_polymer": {
        "unsaturated": {
            "description": "Virtual polymer simulation initialization",
            "template": (
                "Digital simulation view of an unsaturated {material} environment ({process_stages}). "
                "Crystal growth progress: {growth_pct}%. "
                "The image displays a completely blank, uniform white field. "
                "No artifacts or particles are present as the simulation initializes. Next milestone: {next_step}."
            ),
            "visual_markers": ["Blank white canvas", "Uniform background", "Empty field", "Initialization state"]
        },
        "labile": {
            "description": "Virtual nucleation initialization",
            "template": (
                "Digital simulation view of the labile phase in {material} ({process_stages}). "
                "Crystal growth progress: {growth_pct}%. "
                "Sparse, pixelated artifacts resembling small crosses or diamonds are scattered on the white field. "
                "These digital seeds represent stochastic nucleation. Next milestone: {next_step}."
            ),
            "visual_markers": ["Pixelated crosses", "Digital noise", "Sparse distribution", "Small artifacts", "Stochastic seeds"]
        },
        "intermediate": {
            "description": "Virtual growth algorithm execution",
            "template": (
                "Digital simulation view of the intermediate phase in {material} during {process_stages}. "
                "Crystal growth progress: {growth_pct}%. "
                "Distinct circular or globular clusters are growing outward. "
                "The simulation shows enlarged cellular discs with white space between units. Next milestone: {next_step}."
            ),
            "visual_markers": ["Circular clusters", "Globular shapes", "Cellular discs", "Separated growth", "Expanding regions"]
        },
        "metastable": {
            "description": "Virtual simulation completion",
            "template": (
                "Digital simulation view of the metastable phase in {material} ({process_stages}). "
                "Crystal growth progress: {growth_pct}%. "
                "A complete, interlocking tessellation of irregular polygons forms a Voronoi-like pattern. "
                "The field is fully populated with sharp boundaries. Next milestone: {next_step}."
            ),
            "visual_markers": ["Voronoi tessellation", "Interlocking polygons", "Full coverage", "Geometric mosaic", "Complete growth"]
        }
    }
}


# HELPER FUNCTIONS


def estimate_growth_percentage(phase: str, image_index: int = None, total_images: int = None) -> Dict:
    """
    Estimate crystal growth percentage based on phase and optional position within phase.
    
    For more accurate estimation:
    - If image_index and total_images are provided, interpolates within the phase range
    - Otherwise, returns the average for the phase
    """
    growth_info = GROWTH_STAGES.get(phase)
    if not growth_info:
        return {"percentage": 0, "range": (0, 0), "description": "Unknown phase"}
    
    min_pct, max_pct = growth_info.growth_percentage_range
    
    if image_index is not None and total_images is not None and total_images > 0:
        # Interpolate within the phase range based on image position
        progress = image_index / total_images
        estimated_pct = int(min_pct + (max_pct - min_pct) * progress)
    else:
        # Use cumulative average
        estimated_pct = growth_info.cumulative_growth
    
    return {
        "percentage": estimated_pct,
        "range": (min_pct, max_pct),
        "description": growth_info.growth_rate_description,
        "cumulative": growth_info.cumulative_growth
    }

def get_process_stages_for_phase(phase: str) -> List[str]:
    """Get the process stages (from the 10 stages) that correspond to this phase."""
    growth_info = GROWTH_STAGES.get(phase)
    if growth_info:
        return growth_info.process_stage_mapping
    return []

def get_next_step(phase: str) -> str:
    """Get the next step/milestone for the given phase."""
    growth_info = GROWTH_STAGES.get(phase)
    if growth_info:
        return growth_info.next_step
    return "Unknown"

def find_folder_insensitive(base_path: Path, target_name: str) -> Optional[Path]:
    """Finds a folder ignoring case."""
    if not base_path.exists():
        return None
    
    exact_match = base_path / target_name
    if exact_match.exists() and exact_match.is_dir():
        return exact_match

    for item in base_path.iterdir():
        if item.is_dir() and item.name.lower() == target_name.lower():
            return item
            
    return None

def get_images_in_folder(path: Path) -> List[Path]:
    """Get all valid images in a folder (recursive)."""
    images = []
    if not path or not path.exists():
        return images

    for file_path in path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in VALID_EXTENSIONS:
            images.append(file_path)
    return sorted(images)


# CAPTION GENERATION


def generate_enhanced_caption(
    phase: str, 
    material_key: str, 
    material_name: str, 
    image_name: str,
    image_index: int = None,
    total_images_in_phase: int = None,
    image_path: str = None
) -> Dict:
    """
    Generate comprehensive caption with growth percentage and process mapping.
    
    Returns a dictionary with:
    - Basic image info
    - Phase and process stage information
    - Crystal growth percentage estimation
    - Next step recommendation
    - Visual markers
    - Verification status
    """
    
    # Get template configuration
    if material_key not in MATERIAL_SPECIFIC_TEMPLATES:
        visual_config = {
            "template": "Image of {material} in {phase} phase. Growth: {growth_pct}%. Next: {next_step}.", 
            "visual_markers": [],
            "description": "Unknown material configuration"
        }
    else:
        visual_config = MATERIAL_SPECIFIC_TEMPLATES[material_key][phase]
    
    # Get growth information
    growth_info = estimate_growth_percentage(phase, image_index, total_images_in_phase)
    
    # Get process stage mapping
    process_stages = get_process_stages_for_phase(phase)
    process_stages_str = " / ".join([s.replace("_", " ").title() for s in process_stages])
    
    # Get next step
    next_step = get_next_step(phase)
    
    # Get growth stage info for additional details
    growth_stage = GROWTH_STAGES.get(phase)
    
    # Format caption
    caption = visual_config["template"].format(
        material=material_name,
        phase=phase,
        process_stages=process_stages_str,
        growth_pct=growth_info["percentage"],
        next_step=next_step
    )
    
    return {
        # Basic image info
        "image": image_name,
        "image_path": str(image_path) if image_path else None,
        "category_id": material_key,
        "category_name": material_name,
        
        # Phase information
        "phase": phase,
        "phase_description": visual_config.get("description", ""),
        
        # Process stage mapping (10 stages)
        "process_stages": process_stages,
        "process_stages_display": process_stages_str,
        
        # Crystal growth information
        "crystal_growth": {
            "estimated_percentage": growth_info["percentage"],
            "percentage_range": list(growth_info["range"]),
            "growth_description": growth_info["description"],
            "cumulative_growth_avg": growth_info["cumulative"]
        },
        
        # Next step information
        "next_step": next_step,
        "expected_visual_changes": growth_stage.expected_visual_changes if growth_stage else [],
        
        # Caption and markers
        "initial_caption": caption,
        "visual_markers": visual_config["visual_markers"],
        
        # Verification status (for LLM cross-validation)
        "llm_verification_status": "pending",
        "verification_prompts_ready": True,
        
        # Metadata
        "timestamp": datetime.now().isoformat(),
        "generator_version": "2.0"
    }


# DATASET PROCESSING


def process_dataset() -> Tuple[List[Dict], Dict]:
    """Process the entire dataset and generate captions."""
    
    print("=" * 80)
    print("Crystallization Image Caption Generation (VER2)")
    print("With Growth Percentage & Process Stage Mapping")
    print("=" * 80)
    print(f"Dataset Root: {DATASET_ROOT}\n")
    
    if not DATASET_ROOT.exists():
        print(f"[ERROR] Dataset root not found at: {DATASET_ROOT}")
        return [], {}

    all_captions = []
    statistics = {
        "total_images": 0,
        "by_material": {},
        "by_phase": {},
        "growth_statistics": {},
        "errors": []
    }
    
    for material_key, material_human_name in MATERIALS.items():
        material_path = find_folder_insensitive(DATASET_ROOT, material_key)
        
        if not material_path:
            print(f"[WARNING] Folder not found: {material_key} (Skipping...)")
            continue
            
        print(f"\n{'─' * 80}")
        print(f"Processing: {material_human_name}")
        print(f"Path: {material_path}")
        print("─" * 80)
        
        statistics["by_material"][material_key] = {
            "material_name": material_human_name,
            "total_images": 0,
            "by_phase": {}
        }
        
        for phase_key in ["unsaturated", "labile", "intermediate", "metastable"]:
            phase_path = find_folder_insensitive(material_path, phase_key)
            
            if not phase_path:
                print(f"  {phase_key.upper():15} : [NOT FOUND]")
                continue

            images = get_images_in_folder(phase_path)
            image_count = len(images)
            
            # Get growth info for display
            growth_info = GROWTH_STAGES.get(phase_key)
            growth_range = growth_info.growth_percentage_range if growth_info else (0, 0)
            
            print(f"  {phase_key.upper():15} : {image_count:4} images | Growth: {growth_range[0]}-{growth_range[1]}%")
            
            # Update statistics
            statistics["total_images"] += image_count
            statistics["by_material"][material_key]["total_images"] += image_count
            statistics["by_material"][material_key]["by_phase"][phase_key] = image_count
            
            if phase_key not in statistics["by_phase"]:
                statistics["by_phase"][phase_key] = 0
            statistics["by_phase"][phase_key] += image_count
            
            # Generate captions
            try:
                for idx, image_file in enumerate(images):
                    caption_data = generate_enhanced_caption(
                        phase=phase_key,
                        material_key=material_key,
                        material_name=material_human_name,
                        image_name=image_file.name,
                        image_index=idx,
                        total_images_in_phase=image_count,
                        image_path=image_file
                    )
                    all_captions.append(caption_data)
            except Exception as e:
                error_msg = f"Error processing {phase_path}: {str(e)}"
                print(f"    [ERROR] {error_msg}")
                statistics["errors"].append(error_msg)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Images: {statistics['total_images']}")
    print(f"\nBy Phase (with growth ranges):")
    for phase, count in statistics["by_phase"].items():
        growth_info = GROWTH_STAGES.get(phase)
        if growth_info:
            print(f"  {phase:15} : {count:4} images | Growth: {growth_info.growth_percentage_range[0]}-{growth_info.growth_percentage_range[1]}%")
    
    return all_captions, statistics

def save_captions(captions: List[Dict], statistics: Dict) -> None:
    """Save generated captions to JSON files."""
    
    os.makedirs(FILTER_OUTPUT / "annotated_captions_VER2", exist_ok=True)
    
    # Save all captions
    all_captions_file = FILTER_OUTPUT / "all_captions_VER2.json"
    with open(all_captions_file, 'w', encoding='utf-8') as f:
        json.dump(captions, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] All captions saved to: {all_captions_file}")
    
    # Save by phase
    captions_by_phase = {}
    for caption in captions:
        phase = caption["phase"]
        if phase not in captions_by_phase:
            captions_by_phase[phase] = []
        captions_by_phase[phase].append(caption)
    
    for phase, phase_captions in captions_by_phase.items():
        phase_file = FILTER_OUTPUT / "annotated_captions_VER2" / f"{phase}_captions_VER2.json"
        with open(phase_file, 'w', encoding='utf-8') as f:
            json.dump(phase_captions, f, indent=2, ensure_ascii=False)
        print(f"[OK] {phase} captions saved: {len(phase_captions)} items")
    
    # Save statistics
    stats_file = FILTER_OUTPUT / "generation_statistics_VER2.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(statistics, f, indent=2, ensure_ascii=False)
    print(f"[OK] Statistics saved to: {stats_file}")


# MAIN


def main():
    try:
        captions, statistics = process_dataset()
        if captions:
            save_captions(captions, statistics)
            print("\n" + "=" * 80)
            print("[SUCCESS] Caption Generation Complete!")
            print("=" * 80)
            print("\nNext Steps:")
            print("1. Run llm_verification.py to cross-validate captions with BLIP-2")
            print("2. Review generated captions in 'annotated_captions_VER2 folder")
        else:
            print("\n[WARNING] No captions were generated.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
