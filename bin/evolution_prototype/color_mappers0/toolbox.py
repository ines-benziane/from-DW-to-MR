import matplotlib.pyplot as plt
import numpy as np
from cmcrameri import cm
import sys
sys.path.append("..")
from color_mappers import get_color_from_T2_mean, T2_MEAN_MIN, T2_MEAN_MAX

# --- 1. Bande vikO brute (référence) ---
x = np.linspace(0, 1, 256)
plt.figure(figsize=(14, 2))
plt.imshow([cm.vikO(x)], aspect='auto')
plt.xticks(np.linspace(0, 256, 21), [f"{v:.2f}" for v in np.linspace(0, 1, 21)])
plt.title("vikO brute (0 → 1)")
plt.yticks([])

# --- 2.  colorbar T2 custom ---
t2_values = np.linspace(T2_MEAN_MIN, T2_MEAN_MAX, 512)
colors = []
for t2 in t2_values:
    rgb_str = get_color_from_T2_mean(t2, "vikO")
    # Parse "rgb(r, g, b)" → [r/255, g/255, b/255]
    nums = rgb_str.replace("rgb(", "").replace(")", "").split(",")
    colors.append([int(n.strip()) / 255 for n in nums])

colors = np.array([colors])  # shape (1, 512, 3)

plt.figure(figsize=(14, 2))
plt.imshow(colors, aspect='auto')
plt.xticks(np.linspace(0, 512, 11), [f"{v:.0f} ms" for v in np.linspace(T2_MEAN_MIN, T2_MEAN_MAX, 11)])
plt.title("colorbar T2 custom")
plt.yticks([])

plt.tight_layout()
plt.show()