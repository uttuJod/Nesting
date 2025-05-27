# 🧬 OptiLAM Nesting Optimization using Genetic Algorithms

This project implements a Genetic Algorithm (GA) to optimize the nesting of sliced 3D layers (in SVG format) for Laminated Object Manufacturing (LOM), specifically for the OptiLAM process developed at IIT Bombay.

---

## 🧩 Project Overview

Laminated Additive Manufacturing (LOM) slices 3D models into 2D layers which are cut and pasted from sheet rolls. Up to 80% of material is wasted due to poor nesting. This project aims to reduce that by optimally placing and rotating each 2D layer on a 400×400mm canvas, using genetic algorithms.

---

## 🗂️ Project Structure
input_svgs/ # Raw sliced layers (SVG format)  
output_svgs/ # Normalized, rotated SVGs  
output_bmps/ # Preprocessed BMPs for overlap checking  
svg_rotator.py # Preprocesses SVGs: rotation + BMP conversion  
svg_placer.py # Assembles final SVG layout from GA output  
FitnessEvaluator.cs # External evaluator (C# + OpenCV)  
GeneticAlgorithm.hl # Heuristically setup file  
README.md # Project description  

---

## 🔁 Workflow Summary

1. **Slice 3D Model** into `n` SVG layers (e.g., from Fusion360 or Blender).
2. **Run `svg_rotator.py`**:
   - Normalizes and rotates each SVG
   - Converts into BMP for quick pixel-based overlap detection
3. **Launch HeuristicLab**:
   - Load `GeneticAlgorithm.hl`
   - Each chromosome encodes: `x, y, rotation` for each part
   - Evaluates via `FitnessEvaluator.exe` (compiled from `FitnessEvaluator.cs`)
4. **Fitness Evaluation**:
   - BMPs are virtually placed on a canvas
   - Overlaps = negative fitness
   - Tight packing = positive fitness
5. **Run `svg_placer.py`**:
   - Combines optimized placements into final `final_assembled.svg`
   - This becomes input to laser cutter or OptiLAM hardware

---

## 📐 Optimization Goal

- **Maximize nesting efficiency**
- **Avoid overlaps or out-of-bounds placement**
- **Minimize used canvas length (Y direction)**

---

## ⚙️ Requirements



### 🐍 Python (for preprocessing)
- Python 3.8+
- `numpy`, `Pillow`, `lxml`, `opencv-python`, `cairosvg`

### 🪟 C# (for evaluation)
- .NET SDK
- OpenCvSharp4

### 🧬 HeuristicLab (v3.3+)
- Install: https://dev.heuristiclab.com/

---

## 📝 Reference

> Dileep Devarajan, Sudhanshu Dubey, K. P. Karunakaran   
> **Nesting Algorithms for Optimal Laminated Additive Manufacturing**  

