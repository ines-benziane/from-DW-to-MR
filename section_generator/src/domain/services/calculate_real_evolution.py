"""Calculate T2 evolution between data01 and data03"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from domain.entities.t2_stats import T2Stats
from domain.entities.muscle_evolution import MuscleEvolution

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_muscle_t2_average(data, muscle_id, side):
    """Get average T2 for a muscle across all slices"""
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

muscles = set()
for result in data01['results']:
    for muscle in result['muscles']:
        muscles.add((muscle['id'], muscle['side']))

print("="*70)
print("EVOLUTION T2: data01 (old) -> data03 (new)")
print("="*70)

evolutions = []

for muscle_id, side in sorted(muscles):
    old_t2 = get_muscle_t2_average(data01, muscle_id, side)
    new_t2 = get_muscle_t2_average(data03, muscle_id, side)

    if old_t2 is None or new_t2 is None:
        continue

    old_stats = T2Stats(mean=old_t2, sd=0)
    new_stats = T2Stats(mean=new_t2, sd=0)

    evolution = MuscleEvolution(old=old_stats, new=new_stats)
    evolutions.append((muscle_id, side, evolution))

    status_symbol = {
        'degradation': '[!!!]',
        'stable': '[ = ]',
        'improvement': '[ + ]'
    }

    symbol = status_symbol[evolution.evolution_status]
    print(f"{symbol} {muscle_id}-{side}: {old_t2:5.1f} -> {new_t2:5.1f} ({evolution.percentage_change:+6.2f}%) [{evolution.evolution_status}]")

print("="*70)

degraded = [e for _, _, e in evolutions if e.evolution_status == 'degradation']
improved = [e for _, _, e in evolutions if e.evolution_status == 'improvement']
stable = [e for _, _, e in evolutions if e.evolution_status == 'stable']

print(f"\nRESUME:")
print(f"  Degradation (>= +5%): {len(degraded)} muscles")
print(f"  Stable (< 5%):        {len(stable)} muscles")
print(f"  Improvement (>= -5%): {len(improved)} muscles")
print("="*70)
