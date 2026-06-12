# 🌌 3D Solar System Mission Control
> **3D Graphics Final Project — WSB Merito Wrocław**  
> **Student:** Hüseyin Tunay Çelik | **Student ID:** 97294  
> **Course:** 3D Graphics | **Lecturer:** Vishnu Suresh  

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![OpenGL](https://img.shields.io/badge/OpenGL-3.3%20%2F%20Fixed-orange.svg?logo=opengl&logoColor=white)](https://www.opengl.org/)
[![GLFW](https://img.shields.io/badge/GLFW-Windowing-green.svg)](https://www.glfw.org/)
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Project Overview

An interactive, high-fidelity **3D Solar System Simulator** built in Python using PyOpenGL and GLFW. The application goes beyond basic spheres to model a premium Keplerian orbital physics simulator with photorealistic NASA textures, custom atmospheric glow effects, dynamic lighting, a transparent Saturn ring system, and a comprehensive cyber-themed HUD display.

---

## 🚀 Key Features & Upgrades

### 1. Photorealistic NASA Visuals
* **HD Textures:** High-resolution diffuse maps dynamically downloaded and mapped onto the Sun, all 8 planets, the Moon, and a cosmic skyfield.
* **Min/Mag Mipmapping:** PyOpenGL `GL_LINEAR_MIPMAP_LINEAR` filtering minimizes texture aliasing at extreme zoom-out levels, maintaining clean detail as you move the camera.
* **Atmospheric Sun Glow:** Multiple blended, translucent layers surrounding the Sun create a realistic corona. The rendering implements depth-buffer writing controls (`glDepthMask(GL_FALSE)`) to eliminate rendering glitches and prevent depth-buffer clipping.
* **Transparent Saturn Rings:** The ring system extracts texture data from Cassini mission color maps. Brightness levels are mathematically converted to soft alpha-channel values to dynamically render real Cassini and Encke divisions.

### 2. Mathematics & Orbit Inclination
* **Tilted Orbital Planes:** Orbits do not lie on a flat 2D plane. Each celestial body is modeled with its correct inclination angle ($i$) relative to the ecliptic plane, tilting its orbit ring in full 3D space:
  $$\begin{aligned}
  x_{tilted} &= x \cdot \cos(i) \\
  y_{tilted} &= -z \cdot \sin(i) \\
  z_{tilted} &= z \cdot \cos(i)
  \end{aligned}$$
* **Keplerian Hierarchy:** The Moon orbits the Earth using relative matrix transformations (`glPushMatrix` / `glPopMatrix`) while the Earth is inclined relative to the Sun.

### 3. Smooth Camera Glide (Smoothstep)
* Switching targets triggers a smooth camera glide instead of an abrupt jump.
* The translation path uses a standard cubic **smoothstep** interpolation curve to transition between coordinate systems:
  $$f(t) = 3t^2 - 2t^3 \quad \text{for } t \in [0, 1]$$
  This delivers natural acceleration and deceleration (ease-in-ease-out) as the camera locks onto planets.

### 4. Interactive HUD & Controls
* **Hybrid Navigation:** Features both Orbit Trackball (orbital lock-on target) and Free-flight mode (flight controls).
* **Cyber HUD Panel:** Draws telemetry data in real-time, including elapsed simulation time, current time scale factor, camera speed, active flight mode, and selected target metrics.

---

## 📁 Repository Structure

```
├── main.py                          # Main simulator application
├── package_project.py               # Automation script for clean packaging
├── create_final_presentation.py     # Script that builds the PPTX slideshow
├── presentation_speech.md           # Spoken presentation script & guide
├── 3D_Graphics_Final_Presentation.pptx # Generated final presentation
├── .gitignore                       # Standard rules ignoring textures & build cache
└── README.md                        # This documentation
```

---

## 🛠️ Technical Stack

* **Python 3.11+**
* **PyOpenGL / PyOpenGL-Accelerate** — Low-level GPU bindings, material properties, and fixed-function lighting pipeline.
* **GLFW** — High-performance window creation, context binding, and keyboard/mouse event listener callbacks.
* **GLU** — Sphere quadrics rendering, perspective projection, and camera LookAt helper functions.
* **Pillow (PIL)** — Dynamic asset downloader, image decoding, vertical flipping, and channel manipulation for alpha transparency.
* **NumPy** — Vector math helper for starfield distribution and coordinate matrix calculations.

---

## 🕹️ Keyboard & Mouse Controls

| Input | Mode | Action |
|---|---|---|
| **Mouse Left Drag** | Orbital | Rotate camera around targeted planet |
| **Scroll Wheel** | Orbital | Zoom in / out (Distance to target) |
| **`1` — `8` Keys** | Any | Lock camera focus onto planets (Mercury to Neptune) |
| **`9` Key** | Any | Focus camera on the Sun |
| **`0` Key** | Any | Focus camera on the Moon |
| **`R` Key** | Any | Reset camera focus and reset simulation time |
| **`P` Key** | Any | Pause / Resume orbit simulation |
| **`+` / `-` Keys** | Any | Speed up / Slow down simulation speed factor |
| **`TAB` Key** | Any | Toggle between Orbital Camera and Free-Flight Camera |
| **`W` / `S` Keys** | Free-Flight | Move camera Forward / Backward |
| **`A` / `D` Keys** | Free-Flight | Strafe camera Left / Right |
| **`SPACE` / `CTRL`**| Free-Flight | Move camera Up / Down |
| **`ESC` Key** | Any | Exit the application |

---

## 💻 Setup & Execution

### 1. Pre-requisites
Ensure Python is installed on your machine. Install all dependencies:
```bash
pip install pyopengl pyopengl-accelerate glfw numpy pillow
```

### 2. Run the application
Run the main script to start the simulator. If offline, the simulator will automatically use high-fidelity procedural materials:
```bash
python main.py
```

*Note: On first run, missing planetary texture files will be downloaded automatically to the `textures/` directory via a secure HTTPS loader.*

---

## 📄 License

This project is licensed under the MIT License - see the `.gitignore` file for exclusions.
