import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from domain.entities.t2_stats import T2Stats
from domain.entities.muscle_evolution import MuscleEvolution
from infrastructure.color_mappers.crameri_color_mapper import get_evolution_color_from_palette

def load_json(filepath):
    with open (filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_muscle_t2_average(data, muscle_id, side):
    """Calculates T2 mean of all slices for on muscle"""
    t2_values = []
    for result in data['results']:
        for muscle in result['muscles']:
            if muscle['id'] == muscle_id and muscle['side'] == side:
                t2_values.append(muscle['stats']['T2-mean'])
    if not t2_values:
        return None
    return sum(t2_values) / len(t2_values)

data01 = load_json("data/data01.json")
data03 = load_json("data/data03.json")


def get_evolution_color(evolution, palette='broc'):
    """
    Return color according to evolution using scientific palette

    Args:
        evolution: MuscleEvolution object
        palette: 'broc', 'roma', 'vik', 'berlin', 'cork', or 'bam'
    """
    return get_evolution_color_from_palette(evolution, palette_name=palette)

def generate_evolution_svg(data, evolution_dict, output_path, slice_number=3, palette='broc'):
    """
    Generate SVG with muscles colored by evolution using scientific palette

    Args:
        data: JSON data
        evolution_dict: Dictionary of evolutions {(muscle_id, side): MuscleEvolution}
        output_path: Path to save SVG
        slice_number: Which slice to use for contours (default: 3)
        palette: Scientific palette name (default: 'broc')
                 Options: 'broc', 'roma', 'vik', 'berlin', 'cork', 'bam'
    """
    
    slice_index = slice_number - 1
    slice_data = data['results'][slice_index]
    
    contour_path = slice_data['slices']['contour']
    
    svg_parts = []
    svg_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    svg_parts.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="800" height="800">')

    # Fond blanc
    svg_parts.append('<rect width="600" height="600" fill="white"/>')

    svg_parts.append(f'<path d="{contour_path}" fill="none" stroke="gray" stroke-width="2"/>')
    
    for muscle in slice_data['muscles']:
        muscle_id = muscle['id']
        side = muscle['side']
        key = (muscle_id, side)
        
        if key in evolution_dict:
            evolution = evolution_dict[key]
            color = get_evolution_color(evolution, palette=palette)
        else:
            color = "lightgray"  
        
        muscle_path = muscle['path']
        svg_parts.append(f'<path d="{muscle_path}" fill="{color}" fill-opacity="0.7" stroke="black" stroke-width="0.5"/>')
    
    svg_parts.append('</svg>')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg_parts))
    
    print(f"SVG generated: {output_path}")


muscles = set()
for result in data01['results']:
    for muscle in result['muscles']:
        muscles.add((muscle['id'], muscle['side']))

evolutions_dict = {}

for muscle_id, side in muscles:
    old_t2 = get_muscle_t2_average(data01, muscle_id, side)
    new_t2 = get_muscle_t2_average(data03, muscle_id, side)
    
    if old_t2 is not None and new_t2 is not None:
        old_stats = T2Stats(mean=old_t2, sd=0)
        new_stats = T2Stats(mean=new_t2, sd=0)
        evolution = MuscleEvolution(old=old_stats, new=new_stats)
        evolutions_dict[(muscle_id, side)] = evolution

# Generate SVG with different palettes
# Use more alarming colors for medical data (red = danger/degradation)
palettes = ['vik', 'berlin', 'cork']

print("\nGenerating SVGs with scientific palettes...")
print("=" * 50)

for palette_name in palettes:
    output_file = f"evolution_map_{palette_name}.svg"
    generate_evolution_svg(data03, evolutions_dict, output_file, slice_number=3, palette=palette_name)
    print(f"  - {palette_name}: {output_file}")

print("=" * 50)
print("Done!")


