# Cyberpunk Particle System

<div align="center">

![Three.js](https://img.shields.io/badge/Three.js-r128-black?style=for-the-badge&logo=three.js)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands-blue?style=for-the-badge&logo=google)
![Fingerpose](https://img.shields.io/badge/Fingerpose-0.1.0-purple?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A stunning cyberpunk-themed interactive particle system controlled by hand gestures**

[Features](#features) • [Demo](#demo) • [Quick Start](#quick-start) • [Interactions](#interactions) • [Tech Stack](#tech-stack)

</div>

---

## Overview

This project creates an immersive **12,000-particle system** that responds to your hand gestures in real-time. Using computer vision and gesture recognition, you can transform particles into text, scatter them across 3D space, and even form a rotating basketball in your palm.

Built with **Three.js** for rendering, **MediaPipe Hands** for hand tracking, and **Fingerpose** for gesture classification.

## Demo

> Add your demo GIF or video here

```
┌─────────────────────────────────────────────────────────────┐
│  FPS: 60          ┌──────────────┐         LEFT: DETECTED   │
│  PARTICLES: 12000 │              │        RIGHT: DETECTED   │
│  MODE: TEXT_MODE  │    Hello     │         FINGERS: 1 / 0   │
│                   │   ░░▓▓██▓▓░░ │                          │
│                   │              │                          │
│                   └──────────────┘                          │
│                                                             │
│                        [1 FINGER] "Hello" - Neon Blue       │
│                        [2 FINGERS] "Gemini3" - Neon Yellow  │
│                        [RIGHT OPEN] Nebula Mode             │
└─────────────────────────────────────────────────────────────┘
```

## Features

- **12,000 Particles** - High-performance particle system with smooth animations
- **Real-time Hand Tracking** - Powered by MediaPipe Hands (supports 2 hands)
- **Gesture Recognition** - Accurate finger counting using Fingerpose library
- **Multiple Text Modes** - Switch between different texts with finger gestures
- **Nebula Mode** - Scatter particles into 3D space with water ripple effects
- **Basketball Mode** - Form a rotating 3D basketball that wraps around your hand
- **Cyberpunk Aesthetics** - Neon colors, scanlines, grid overlay, and vignette effects
- **Live Camera Background** - Your webcam feed as a semi-transparent backdrop
- **Responsive HUD** - Real-time display of FPS, particle count, and hand status

## Quick Start

### Prerequisites

- Modern web browser with WebGL support
- Webcam access
- Python 3.x (for local server) or any HTTP server

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/cyberpunk-particle-system.git
   cd cyberpunk-particle-system
   ```

2. **Start a local server**
   ```bash
   python3 -m http.server 8003
   ```

3. **Open in browser**
   ```
   http://localhost:8003
   ```

4. **Allow camera access** when prompted

## Interactions

### Left Hand - Command Controller

Control the particle formation with your left hand:

| Fingers | Text | Color |
|---------|------|-------|
| 1 | "Hello" | Neon Cyan `#00FFFF` |
| 2 | "Gemini3" | Neon Yellow `#FFFF00` |
| 3 | "非常好用" | Neon Pink `#FF00FF` |
| 4 | "再见" | Neon Green `#00FF88` |
| 5 | **Catch Mode** | - |

### Right Hand - Physics Interactor

| Gesture | Effect |
|---------|--------|
| Point / Fist | **Scatter** - Repel particles on contact (XY plane only) |
| Open Hand (5 fingers) | **Nebula Mode** - Particles fill 3D space with water ripple effect |

### Dual Hand Combo - Ultimate Effect

| Condition | Effect |
|-----------|--------|
| Both hands open | **Basketball Mode** - All particles fly to your left palm and form a rotating 3D basketball with bouncing trajectory animation |

## Tech Stack

| Technology | Purpose |
|------------|---------|
| [Three.js](https://threejs.org/) | WebGL 3D rendering engine |
| [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html) | Real-time hand landmark detection |
| [Fingerpose](https://github.com/andypotato/fingerpose) | Gesture recognition & classification |
| HTML5 Canvas | Text-to-particle coordinate generation |
| WebRTC | Camera stream access |

## Configuration

All parameters can be adjusted in the `CONFIG` object:

```javascript
const CONFIG = {
    PARTICLE_COUNT: 12000,      // Number of particles
    PARTICLE_SIZE: 2.4,         // Size of each particle
    LERP_FACTOR: 0.28,          // Movement speed (0-1)
    REPULSION_STRENGTH: 0.8,    // Scatter force intensity
    REPULSION_RADIUS: 0.15,     // Scatter effect radius
    TEXT_CONFIGS: {             // Customize text and colors
        1: { text: 'Hello', color: 0x00FFFF },
        2: { text: 'Gemini3', color: 0xFFFF00 },
        3: { text: '非常好用', color: 0xFF00FF },
        4: { text: '再见', color: 0x00FF88 }
    },
    BASKETBALL_COLOR: 0xFF8800  // Basketball color
};
```

## Project Structure

```
cyberpunk-particle-system/
├── index.html          # Single-file application (HTML + CSS + JS)
├── README.md           # Documentation
└── LICENSE             # MIT License
```

## Browser Compatibility

| Browser | Support |
|---------|---------|
| Chrome | ✅ Recommended |
| Firefox | ✅ Supported |
| Edge | ✅ Supported |
| Safari | ⚠️ Limited (WebGL issues) |

## Performance Tips

- Close other browser tabs for better performance
- Ensure good lighting for hand detection
- Keep hands within camera frame
- Use Chrome for best experience

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Three.js](https://threejs.org/) - Amazing 3D library
- [MediaPipe](https://mediapipe.dev/) - Powerful ML solutions
- [Fingerpose](https://github.com/andypotato/fingerpose) - Gesture recognition made easy

---

<div align="center">

**Made with ❤️ and lots of particles**

⭐ Star this repo if you like it!

</div>
