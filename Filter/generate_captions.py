import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

BASE_PATH = Path(__file__).parent
DATASET_ROOT = BASE_PATH / "_21p1_pjirayu_Seed-Crystallization-Dataset" / "balanced_crystallization"
FILTER_OUTPUT = BASE_PATH / "Filter"

# Allowed image extensions (Case Insensitive)
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}

PROCESS_FLOW = {
    "unsaturated": {
        "current_steps": "Charging / Concentration",
        "description": "Initial evaporation stage prior to nucleation",
        "next_milestone": "Seeding"
    },
    "labile": {
        "current_steps": "Seeding / Graining",
        "description": "Grain establishment and initial nucleation",
        "next_milestone": "Boiling (Growth)"
    },
    "intermediate": {
        "current_steps": "Boiling / Boiling_hold / Boiling_end",
        "description": "Main crystal growth operation",
        "next_milestone": "Tightening"
    },
    "metastable": {
        "current_steps": "Tightening / Discharge",
        "description": "Final density increase and batch completion",
        "next_milestone": "Batch Complete"
    }
}

MATERIAL_SPECIFIC_TEMPLATES = {
    # --------------------------------------------------------------------------
    # Physical Sugar Dense Batch (phy_sugar_db)
    # --------------------------------------------------------------------------
    "phy_sugar_db": {
        "unsaturated": {
            "description": "Dense sugar solution below saturation",
            "template": "Microscopic view of an unsaturated {material} solution during the {steps} stage. "
                       "The image displays a uniform, featureless amber background indicating a homogeneous liquid phase. "
                       "No crystal structures or particles are visible as the system prepares for {next_step}.",
            "visual_markers": ["Homogeneous amber background", "Featureless liquid", "No particles"]
        },
        "labile": {
            "description": "Initial seeding in dense batch",
            "template": "Microscopic view of the labile phase in {material} ({steps}). "
                       "The image shows a dark field populated by sparse, minute bright specks. "
                       "These isolated points of light represent the initial nucleation event transitioning toward {next_step}.",
            "visual_markers": ["Dark background", "Tiny scattered bright specks", "Initial nucleation"]
        },
        "intermediate": {
            "description": "Active growth in dense batch",
            "template": "Microscopic view of the intermediate crystallization phase in {material} during {steps}. "
                       "Distinct, sharply defined rectangular and prismatic crystal shapes are clearly visible. "
                       "The crystals are varying in size with separation between structures, progressing toward {next_step}.",
            "visual_markers": ["Rectangular prisms", "Defined edges", "Separated crystals", "Geometric shapes"]
        },
        "metastable": {
            "description": "Final stage dense batch",
            "template": "Microscopic view of the metastable phase in {material} ({steps}). "
                       "The frame is completely filled with a dense, interlocking mosaic of fully formed crystals. "
                       "Large, faceted structures crowd against one another, ready for {next_step}.",
            "visual_markers": ["Interlocking mosaic", "Crowded field", "High density", "No background"]
        }
    },

    # --------------------------------------------------------------------------
    # Physical Sugar Operation (phy_sugar_opr)
    # --------------------------------------------------------------------------
    "phy_sugar_opr": {
        "unsaturated": {
            "description": "Operational sugar solution",
            "template": "Microscopic view of an unsaturated {material} fluid during {steps}. "
                       "The image shows a smooth, light gradient background free of crystalline geometry. "
                       "Only sparse, spherical artifacts (bubbles) are suspended in the liquid prior to {next_step}.",
            "visual_markers": ["Smooth light background", "Spherical bubbles", "No crystal angles"]
        },
        "labile": {
            "description": "Operational seeding phase",
            "template": "Microscopic view of the labile phase in {material} ({steps}). "
                       "Small, irregular dark aggregates and clumps are scattered widely across the frame. "
                       "These distinct clusters indicate the onset of solid formation as the process moves to {next_step}.",
            "visual_markers": ["Scattered dark clumps", "Irregular aggregates", "Wide spacing"]
        },
        "intermediate": {
            "description": "Operational growth phase",
            "template": "Microscopic view of the intermediate crystallization phase in {material} during {steps}. "
                       "Large, translucent cubic and rectangular prisms are floating in the solution. "
                       "The crystals exhibit sharp edges and distinct volume as the system approaches {next_step}.",
            "visual_markers": ["Translucent cubes", "Rectangular prisms", "Sharp straight edges", "3D volume"]
        },
        "metastable": {
            "description": "Operational completion",
            "template": "Microscopic view of the metastable phase in {material} during {steps}. "
                       "A high-density accumulation of bright, opaque crystal structures crowds the view. "
                       "The crystals are heavily overlapped and packed, indicating the cycle is ready for {next_step}.",
            "visual_markers": ["Bright opaque crystals", "Dense packing", "Heavily overlapped", "Textured surface"]
        }
    },

    # --------------------------------------------------------------------------
    # Virtual Polymer (vir_polymer)
    # --------------------------------------------------------------------------
    "vir_polymer": {
        "unsaturated": {
            "description": "Virtual polymer simulation start",
            "template": "Digital simulation view of an unsaturated {material} environment ({steps}). "
                       "The image displays a completely blank, uniform white field. "
                       "No artifacts or particles are present as the algorithm initializes {next_step}.",
            "visual_markers": ["Blank white canvas", "Uniform background", "Empty field"]
        },
        "labile": {
            "description": "Virtual nucleation event",
            "template": "Digital simulation view of the labile phase in {material} ({steps}). "
                       "Sparse, pixelated artifacts resembling small crosses or diamonds are scattered on the white field. "
                       "These digital seeds represent the stochastic initialization of {next_step}.",
            "visual_markers": ["Pixelated crosses", "Digital noise", "Sparse distribution", "Small artifacts"]
        },
        "intermediate": {
            "description": "Virtual growth algorithm",
            "template": "Digital simulation view of the intermediate phase in {material} during {steps}. "
                       "Distinct, circular or globular clusters are growing outward. "
                       "The simulation shows enlarged, cellular discs with white space separating the units before {next_step}.",
            "visual_markers": ["Circular clusters", "Globular shapes", "Cellular discs", "Separated growth"]
        },
        "metastable": {
            "description": "Virtual simulation end",
            "template": "Digital simulation view of the metastable phase in {material} ({steps}). "
                       "A complete, interlocking tessellation of irregular polygons forms a Voronoi-like pattern. "
                       "The field is fully populated with sharp boundaries, signaling the {next_step}.",
            "visual_markers": ["Voronoi tessellation", "Interlocking polygons", "Full coverage", "Geometric mosaic"]
        }
    }
}

MATERIALS = {
    "phy_sugar_db": "Physical Sugar (Dense Batch)",
    "phy_sugar_opr": "Physical Sugar (Operation)",
    "vir_polymer": "Virtual Polymer"
}

def find_folder_insensitive(base_path: Path, target_name: str) -> Path:
    """Finds a folder ignoring case (e.g., finds 'Unsaturated' for 'unsaturated')."""
    if not base_path.exists():
        return None
    
    # 1. Try exact match first
    exact_match = base_path / target_name
    if exact_match.exists() and exact_match.is_dir():
        return exact_match

    # 2. Try case-insensitive scan
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

# def generate_caption(phase: str, material_key: str, material_name: str, image_name: str) -> Dict:
#     """Generate caption using the material-specific template."""
    
#     # 1. Select the correct template set based on material_key
#     if material_key not in MATERIAL_SPECIFIC_TEMPLATES:
#         # Fallback if a new material is added but not defined in templates
#         print(f"[WARN] No template found for {material_key}, using generic error text.")
#         config = {
#             "template": "Image of {material} in {phase} phase.",
#             "description": "Unknown material config",
#             "visual_markers": []
#         }
#     else:
#         # 2. Get the specific phase config for this material
#         config = MATERIAL_SPECIFIC_TEMPLATES[material_key][phase]

#     # 3. Format the template
#     caption = config["template"].format(material=material_name, phase=phase)
    
#     return {
#         "image": image_name,
#         "category_id": material_key,
#         "category_name": material_name,
#         "phase": phase,
#         "phase_description": config["description"],
#         "initial_caption": caption,
#         "visual_markers": config["visual_markers"],
#         "llm_verification_status": "pending",
#         "timestamp": datetime.now().isoformat()
#     }

def generate_caption(phase: str, material_key: str, material_name: str, image_name: str) -> Dict:
    """Generate caption with Process Step integration."""
    
    if material_key not in MATERIAL_SPECIFIC_TEMPLATES:
        visual_config = {
            "template": "Image of {material} in {phase}.", 
            "visual_markers": []
        }
    else:
        visual_config = MATERIAL_SPECIFIC_TEMPLATES[material_key][phase]

    process_info = PROCESS_FLOW.get(phase, {
        "current_steps": "Unknown Step", 
        "next_milestone": "Unknown"
    })

    caption = visual_config["template"].format(
        material=material_name, 
        phase=phase,
        steps=process_info["current_steps"],
        next_step=process_info["next_milestone"]
    )
    
    return {
        "image": image_name,
        "category_id": material_key,
        "category_name": material_name,
        "phase": phase,
        "process_stage": process_info["current_steps"],
        "next_process_stage": process_info["next_milestone"],
        "process_description": process_info["description"],
        "initial_caption": caption,
        "visual_markers": visual_config["visual_markers"],
        "llm_verification_status": "pending",
        "timestamp": datetime.now().isoformat()
    }

def process_dataset() -> Tuple[List[Dict], Dict]:
    print("=" * 70)
    print("Crystallization Image Caption Generation (Specific Material Mode)")
    print("=" * 70)
    print(f"Dataset Root: {DATASET_ROOT}\n")
    
    if not DATASET_ROOT.exists():
        print(f"[ERROR] Dataset root not found at: {DATASET_ROOT}")
        return [], {}

    all_captions = []
    statistics = {
        "total_images": 0,
        "by_material": {},
        "by_phase": {},
        "errors": []
    }
    
    # Iterate through expected materials
    for material_key, material_human_name in MATERIALS.items():
        material_path = find_folder_insensitive(DATASET_ROOT, material_key)
        
        if not material_path:
            print(f"[WARNING] Folder not found: {material_key} (Skipping...)")
            continue
            
        print(f"\nProcessing Category: {material_human_name}")
        print(f"  Folder Found: {material_path.name}")
        print("-" * 70)
        
        statistics["by_material"][material_key] = {
            "material_name": material_human_name,
            "total_images": 0,
            "by_phase": {}
        }
        
        # Iterate through phases
        for phase_key in ["unsaturated", "labile", "intermediate", "metastable"]:
            phase_path = find_folder_insensitive(material_path, phase_key)
            
            if not phase_path:
                print(f"  {phase_key.upper():15} : [NOT FOUND] Folder missing")
                continue

            images = get_images_in_folder(phase_path)
            image_count = len(images)
            
            print(f"  {phase_key.upper():15} : {image_count:3} images")
            
            if image_count == 0:
                print(f"    -> Checked {phase_path}")
                print(f"    -> [WARNING] Folder exists but contains no recognized images!")
            
            statistics["total_images"] += image_count
            statistics["by_material"][material_key]["total_images"] += image_count
            statistics["by_material"][material_key]["by_phase"][phase_key] = image_count
            
            if phase_key not in statistics["by_phase"]:
                statistics["by_phase"][phase_key] = 0
            statistics["by_phase"][phase_key] += image_count
            
            try:
                for image_file in images:
                    caption_data = generate_caption(phase_key, material_key, material_human_name, image_file.name)
                    all_captions.append(caption_data)
            except Exception as e:
                error_msg = f"Error processing {phase_path}: {str(e)}"
                print(f"  ERROR: {error_msg}")
                statistics["errors"].append(error_msg)

    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    print(f"Total Images Processed: {statistics['total_images']}")
    print(f"\nBy Material (Category):")
    for mat_key, data in statistics["by_material"].items():
        print(f"  {data['material_name']:30} : {data['total_images']:4} images")
    
    return all_captions, statistics

def save_captions(captions: List[Dict], statistics: Dict) -> None:
    os.makedirs(FILTER_OUTPUT / "annotated_caption", exist_ok=True)
    
    all_captions_file = FILTER_OUTPUT / "all_initial_captions.json"
    with open(all_captions_file, 'w', encoding='utf-8') as f:
        json.dump(captions, f, indent=2, ensure_ascii=False)
    
    captions_by_phase = {}
    for caption in captions:
        phase = caption["phase"]
        if phase not in captions_by_phase:
            captions_by_phase[phase] = []
        captions_by_phase[phase].append(caption)
    
    for phase, phase_captions in captions_by_phase.items():
        phase_file = FILTER_OUTPUT / "annotated_caption" / f"{phase}_captions.json"
        with open(phase_file, 'w', encoding='utf-8') as f:
            json.dump(phase_captions, f, indent=2, ensure_ascii=False)
    
    stats_file = FILTER_OUTPUT / "generation_statistics.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(statistics, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Statistics saved to: {stats_file}")

def main():
    try:
        captions, statistics = process_dataset()
        if captions:
            save_captions(captions, statistics)
            print("\n[SUCCESS] Processing Complete!")
        else:
            print("\n[WARNING] No captions were generated.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()