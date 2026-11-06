/**
 * D.A.E.M.O.N. - 3D Galactic Nebula Core Engine (WebGL2 + Three.js)
 * High-performance GPU-driven volumetric particle system (60,000 - 120,000 particles)
 * Features:
 *  - Procedural Simplex / Curl noise in Vertex Shader
 *  - Additive blending with Gaussian sprite falloff
 *  - Volumetric gas layers with smooth depth attenuation
 *  - Radial audio spectrum ring (64 reactive bands)
 *  - State machine with smooth 300-600ms transitions (idle, listening, thinking, speaking, error, paused)
 *  - Adaptive FPS quality scaler (Auto, Low, Medium, High) with 0% CPU pause when hidden
 *  - 100% offline standalone execution
 */

(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        define(['three'], factory);
    } else if (typeof exports === 'object') {
        module.exports = factory(require('three'));
    } else {
        root.GalacticNebula = factory(root.THREE);
    }
}(typeof self !== 'undefined' ? self : this, function (THREE) {
    'use strict';

    // =========================================================================
    // COLOR THEME PRESETS
    // =========================================================================
    const PALETTES = {
        spectral: {
            name: "Nebulosa Espectral",
            core: new THREE.Color(0x00f5ff),     // Electric Cyan
            inner: new THREE.Color(0x3a40ff),    // Deep Electric Blue
            arms: new THREE.Color(0xb026ff),     // Vivid Violet
            outer: new THREE.Color(0xff2a85),    // Hot Magenta
            sparks: new THREE.Color(0xffd700),   // Solar Gold
            gas: new THREE.Color(0x190b3b)       // Deep cosmic purple
        },
        aurora: {
            name: "Aurora Boreal",
            core: new THREE.Color(0x00ffaa),     // Emerald Mint
            inner: new THREE.Color(0x00c8ff),    // Sky Blue
            arms: new THREE.Color(0x1a75ff),     // Royal Blue
            outer: new THREE.Color(0x8a2be2),    // Indigo
            sparks: new THREE.Color(0xadff2f),   // Electric Lime
            gas: new THREE.Color(0x041824)       // Deep oceanic gas
        },
        gold: {
            name: "Oro Solar / Akatsuki",
            core: new THREE.Color(0xfff2a3),     // Sunlight
            inner: new THREE.Color(0xffaa00),    // Vibrant Amber
            arms: new THREE.Color(0xff4500),     // Plasma Orange
            outer: new THREE.Color(0xd90429),    // Crimson Flame
            sparks: new THREE.Color(0xffe600),   // High Gold
            gas: new THREE.Color(0x280d05)       // Deep magma gas
        },
        monochrome: {
            name: "Monocromo Cyberpunk",
            core: new THREE.Color(0xffffff),     // Pure White
            inner: new THREE.Color(0x90e0ef),    // Ice Blue
            arms: new THREE.Color(0x0077b6),     // Steel Blue
            outer: new THREE.Color(0x48cae4),    // Diamond Glow
            sparks: new THREE.Color(0xe0fbfc),   // Frost Spark
            gas: new THREE.Color(0x05131d)       // Cryogenic gas
        },
        error: {
            name: "Alerta de Error",
            core: new THREE.Color(0xffffff),
            inner: new THREE.Color(0xff2a2a),
            arms: new THREE.Color(0xcc0000),
            outer: new THREE.Color(0x660000),
            sparks: new THREE.Color(0xff9900),
            gas: new THREE.Color(0x300505)
        },
        paused: {
            name: "Modo Pausa",
            core: new THREE.Color(0x6c757d),
            inner: new THREE.Color(0x495057),
            arms: new THREE.Color(0x343a40),
            outer: new THREE.Color(0x212529),
            sparks: new THREE.Color(0xadb5bd),
            gas: new THREE.Color(0x0f1115)
        }
    };

    // =========================================================================
    // GLSL SHADER CODE
    // =========================================================================
    const VERTEX_SHADER = `
        uniform float uTime;
        uniform float uStateTime;
        uniform float uAudioLevel;
        uniform vec3  uAudioBands;     // x: bass, y: mid, z: treble
        uniform float uState;          // 0: idle, 1: listening, 2: thinking, 3: speaking, 4: error, 5: paused
        uniform float uStateTransition; // 0..1 transition progress
        uniform float uPixelRatio;
        uniform float uSizeMultiplier;

        attribute float aSize;
        attribute float aPhase;
        attribute float aRadius;
        attribute float aLayer;        // 0: core, 1: spiral arms, 2: halo, 3: golden sparks
        attribute vec3  aInitialPos;

        varying vec3  vColor;
        varying float vAlpha;
        varying float vLayer;

        uniform vec3 uColorCore;
        uniform vec3 uColorInner;
        uniform vec3 uColorArms;
        uniform vec3 uColorOuter;
        uniform vec3 uColorSparks;

        // 3D Simplex-like noise helper
        vec4 permute(vec4 x) { return mod(((x*34.0)+1.0)*x, 289.0); }
        vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }
        
        float snoise(vec3 v) {
            const vec2 C = vec2(1.0/6.0, 1.0/3.0);
            const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
            vec3 i  = floor(v + dot(v, C.yyy));
            vec3 x0 = v - i + dot(i, C.xxx);
            vec3 g = step(x0.yzx, x0.xyz);
            vec3 l = 1.0 - g;
            vec3 i1 = min(g.xyz, l.zxy);
            vec3 i2 = max(g.xyz, l.zxy);
            vec3 x1 = x0 - i1 + 1.0 * C.xxx;
            vec3 x2 = x0 - i2 + 2.0 * C.xxx;
            vec3 x3 = x0 - 1.0 + 3.0 * C.xxx;
            i = mod(i, 289.0);
            vec4 p = permute(permute(permute(
                i.z + vec4(0.0, i1.z, i2.z, 1.0))
                + i.y + vec4(0.0, i1.y, i2.y, 1.0))
                + i.x + vec4(0.0, i1.x, i2.x, 1.0));
            float n_ = 0.142857142857;
            vec3 ns = n_ * D.wyz - D.xzx;
            vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
            vec4 x_ = floor(j * ns.z);
            vec4 y_ = floor(j - 7.0 * x_);
            vec4 x = x_ *ns.x + ns.yyyy;
            vec4 y = y_ *ns.x + ns.yyyy;
            vec4 h = 1.0 - abs(x) - abs(y);
            vec4 b0 = vec4(x.xy, y.xy);
            vec4 b1 = vec4(x.zw, y.zw);
            vec4 s0 = floor(b0)*2.0 + 1.0;
            vec4 s1 = floor(b1)*2.0 + 1.0;
            vec4 sh = -step(h, vec4(0.0));
            vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy;
            vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;
            vec3 p0 = vec3(a0.xy, h.x);
            vec3 p1 = vec3(a0.zw, h.y);
            vec3 p2 = vec3(a1.xy, h.z);
            vec3 p3 = vec3(a1.zw, h.w);
            vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
            p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;
            vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
            m = m * m;
            return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
        }

        void main() {
            vLayer = aLayer;
            vec3 pos = aInitialPos;

            // 1. Rotation speed depending on state
            float rotSpeed = 0.35;
            if (uState == 1.0) rotSpeed = 0.70;       // listening
            else if (uState == 2.0) rotSpeed = 2.10;  // thinking (fast swirl)
            else if (uState == 3.0) rotSpeed = 0.85;  // speaking
            else if (uState == 5.0) rotSpeed = 0.06;  // paused

            float angle = uTime * rotSpeed * (1.0 / (0.4 + aRadius * 0.7));
            float cosA = cos(angle);
            float sinA = sin(angle);
            vec3 rotatedPos = vec3(
                pos.x * cosA - pos.z * sinA,
                pos.y,
                pos.x * sinA + pos.z * cosA
            );

            // 2. Organic Simplex Turbulence Noise
            float noiseFreq = 0.9;
            float noiseAmp = 0.12 + 0.15 * uAudioLevel;
            if (uState == 2.0) noiseAmp *= 1.8; // thinking turbulence
            vec3 noiseVec = vec3(
                snoise(rotatedPos * noiseFreq + vec3(uTime * 0.4, 0.0, 0.0)),
                snoise(rotatedPos * noiseFreq + vec3(0.0, uTime * 0.4, 0.0)),
                snoise(rotatedPos * noiseFreq + vec3(0.0, 0.0, uTime * 0.4))
            );
            rotatedPos += noiseVec * noiseAmp;

            // 3. State-specific morphing
            // LISTENING: particles contract inward, pulsing with mic
            if (uState == 1.0) {
                float contract = 0.75 + 0.18 * sin(uTime * 5.0) - 0.22 * uAudioLevel;
                rotatedPos.xz *= contract;
            }
            // THINKING: vortex spiral stretching
            else if (uState == 2.0) {
                float spiral = (1.0 - aRadius) * 0.6;
                rotatedPos.y += sin(uTime * 4.0 + aRadius * 8.0) * 0.15;
                rotatedPos.xz *= (1.0 + spiral * 0.3);
            }
            // SPEAKING: radial acoustic ripples
            else if (uState == 3.0) {
                float wave = sin(aRadius * 18.0 - uTime * 10.0) * (uAudioBands.x * 0.35 + uAudioLevel * 0.2);
                rotatedPos += normalize(rotatedPos + 0.001) * wave;
            }
            // IDLE: gentle organic breathing
            else if (uState == 0.0) {
                float breath = 1.0 + 0.04 * sin(uTime * 1.5 + aPhase);
                rotatedPos *= breath;
            }

            // 4. Color Assignment along radial layers
            vec3 col;
            float rNorm = clamp(aRadius / 2.5, 0.0, 1.0);
            if (aLayer == 3.0) {
                // Golden Sparks
                col = uColorSparks * (1.1 + 0.4 * sin(uTime * 6.0 + aPhase));
            } else if (rNorm < 0.22) {
                col = mix(uColorCore, uColorInner, rNorm / 0.22);
            } else if (rNorm < 0.65) {
                col = mix(uColorInner, uColorArms, (rNorm - 0.22) / 0.43);
            } else {
                col = mix(uColorArms, uColorOuter, (rNorm - 0.65) / 0.35);
            }

            // Error state: red flashes
            if (uState == 4.0) {
                col = mix(col, vec3(1.0, 0.1, 0.1), 0.85);
            }

            vColor = col;

            // 5. Dynamic Alpha and Twinkle
            float twinkle = 0.75 + 0.25 * sin(uTime * 3.0 + aPhase * 6.28);
            if (uState == 5.0) twinkle *= 0.35; // dimmed on paused
            vAlpha = twinkle * clamp(1.2 - rNorm * 0.7, 0.15, 1.0);

            // 6. Projection and Size Attenuation by Distance
            vec4 mvPosition = modelViewMatrix * vec4(rotatedPos, 1.0);
            gl_Position = projectionMatrix * mvPosition;

            float depthFactor = 280.0 / -mvPosition.z;
            float stateSizeBonus = 1.0;
            if (uState == 1.0) stateSizeBonus = 1.25 + uAudioLevel * 0.6;
            else if (uState == 3.0) stateSizeBonus = 1.0 + uAudioBands.y * 0.8;

            gl_PointSize = clamp(aSize * depthFactor * uPixelRatio * uSizeMultiplier * stateSizeBonus, 1.2, 48.0);
        }
    `;

    const FRAGMENT_SHADER = `
        precision highp float;
        varying vec3  vColor;
        varying float vAlpha;
        varying float vLayer;

        uniform float uBloomIntensity;

        void main() {
            // Gaussian round sprite with smooth falloff
            vec2 coord = gl_PointCoord - vec2(0.5);
            float distSq = dot(coord, coord);
            if (distSq > 0.25) discard;

            // Soft exponential Gaussian glow curve
            float falloff = exp(-distSq * 18.0);
            float outerHalo = exp(-distSq * 6.0) * 0.35;
            float intensity = (falloff + outerHalo) * vAlpha * (1.0 + uBloomIntensity * 0.8);

            // Center spark core brightening
            vec3 finalColor = vColor;
            if (distSq < 0.04) {
                finalColor += vec3(0.35) * (1.0 - distSq / 0.04);
            }

            gl_FragColor = vec4(finalColor * intensity, intensity);
        }
    `;

    // =========================================================================
    // RADIAL AUDIO RING GLSL SHADER
    // =========================================================================
    const RING_VERTEX_SHADER = `
        uniform float uTime;
        uniform float uAudioLevel;
        uniform float uBass;
        uniform float uTreble;
        uniform float uState;
        attribute float aAngle;
        attribute float aHeight;
        varying vec2 vUv;
        varying float vHeight;

        void main() {
            vUv = uv;
            vHeight = aHeight;
            float r = 2.45 + aHeight * (0.15 + uAudioLevel * 0.45 + uBass * 0.4);
            vec3 pos = vec3(cos(aAngle) * r, aHeight * 0.12, sin(aAngle) * r);
            gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
        }
    `;

    const RING_FRAGMENT_SHADER = `
        precision highp float;
        uniform vec3 uColor;
        uniform float uAlpha;
        varying vec2 vUv;
        varying float vHeight;

        void main() {
            float edge = smoothstep(0.0, 0.4, vHeight) * smoothstep(1.0, 0.6, vHeight);
            gl_FragColor = vec4(uColor * (1.2 + vHeight), uAlpha * (0.3 + edge * 0.7));
        }
    `;

    // =========================================================================
    // CLASS GALACTIC NEBULA
    // =========================================================================
    class GalacticNebula {
        constructor(container, options = {}) {
            this.container = typeof container === 'string' ? document.querySelector(container) : container;
            if (!this.container) {
                throw new Error("Container element not found for GalacticNebula.");
            }

            this.options = Object.assign({
                particleCount: 80000,
                theme: 'spectral',
                quality: 'auto',       // auto, low (30k), medium (60k), high (100k)
                showSpectrumRing: true,
                bloomIntensity: 0.9,
                speedMultiplier: 1.0,
                transparent: true,
                onFpsUpdate: null
            }, options);

            this.state = 'idle';        // idle, listening, thinking, speaking, error, paused
            this.stateNum = 0.0;
            this.targetStateNum = 0.0;
            this.stateTransition = 1.0;
            this.audioLevel = 0.0;
            this.targetAudioLevel = 0.0;
            this.audioBands = { bass: 0.0, mid: 0.0, treble: 0.0 };
            this.currentThemeName = this.options.theme;

            this.clock = new THREE.Clock();
            this.isRunning = true;
            this.isPaused = false;
            this.frameCount = 0;
            this.lastFpsCheck = performance.now();
            this.currentFps = 60;

            this._initScene();
            this._createNebulaParticles();
            this._createGasLayers();
            this._createSpectrumRing();
            this._setupEvents();
            this.setTheme(this.options.theme);
            this.setQuality(this.options.quality);

            this.animate = this.animate.bind(this);
            requestAnimationFrame(this.animate);
        }

        _initScene() {
            const width = this.container.clientWidth || 300;
            const height = this.container.clientHeight || 300;

            // 1. Scene & Camera
            this.scene = new THREE.Scene();
            this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
            this.camera.position.set(0, 2.2, 5.4);
            this.camera.lookAt(0, 0, 0);

            // 2. WebGLRenderer with HighDPI & Translucency
            const canvas = document.createElement('canvas');
            const glContext = canvas.getContext('webgl2') || canvas.getContext('webgl');
            if (!glContext) {
                console.warn("[NEBULA] WebGL not available, falling back to 2D canvas.");
                this._init2DFallback();
                return;
            }

            this.renderer = new THREE.WebGLRenderer({
                canvas: canvas,
                context: glContext,
                alpha: true,
                antialias: true,
                powerPreference: "high-performance",
                precision: "highp"
            });
            this.renderer.setSize(width, height);
            this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2.0));
            this.renderer.setClearColor(0x000000, 0);
            this.container.appendChild(this.renderer.domElement);
        }

        _createNebulaParticles() {
            const count = this.options.particleCount;
            const geometry = new THREE.BufferGeometry();

            const positions = new Float32Array(count * 3);
            const initialPos = new Float32Array(count * 3);
            const sizes = new Float32Array(count);
            const phases = new Float32Array(count);
            const radii = new Float32Array(count);
            const layers = new Float32Array(count);

            const numArms = 3;
            const armAngleStep = (Math.PI * 2) / numArms;

            for (let i = 0; i < count; i++) {
                const i3 = i * 3;
                const rand = Math.random();

                let radius, theta, phi, layer, size;

                if (rand < 0.28) {
                    // DENSE CORE (28%)
                    layer = 0.0;
                    radius = Math.pow(Math.random(), 2.0) * 0.65;
                    theta = Math.random() * Math.PI * 2;
                    phi = (Math.random() - 0.5) * Math.PI * 0.45;
                    size = 1.8 + Math.random() * 2.2;
                } else if (rand < 0.85) {
                    // SPIRAL ARMS (57%)
                    layer = 1.0;
                    const armIndex = i % numArms;
                    const armOffset = armIndex * armAngleStep;
                    radius = 0.55 + Math.pow(Math.random(), 1.2) * 1.85;
                    const spiralTwist = radius * 2.8;
                    const dispersion = (Math.random() - 0.5) * (0.35 / (radius + 0.3));
                    theta = armOffset + spiralTwist + dispersion;
                    phi = (Math.random() - 0.5) * 0.35 * Math.exp(-radius * 0.6);
                    size = 1.2 + Math.random() * 1.9;
                } else if (rand < 0.95) {
                    // DIFFUSE HALO (10%)
                    layer = 2.0;
                    radius = 1.8 + Math.random() * 1.1;
                    theta = Math.random() * Math.PI * 2;
                    phi = (Math.random() - 0.5) * Math.PI * 0.7;
                    size = 0.9 + Math.random() * 1.4;
                } else {
                    // CHAOTIC GOLDEN SPARKS (5%)
                    layer = 3.0;
                    radius = 0.3 + Math.random() * 2.4;
                    theta = Math.random() * Math.PI * 2;
                    phi = (Math.random() - 0.5) * Math.PI;
                    size = 2.4 + Math.random() * 3.0;
                }

                const x = radius * Math.cos(phi) * Math.cos(theta);
                const y = radius * Math.sin(phi);
                const z = radius * Math.cos(phi) * Math.sin(theta);

                positions[i3] = x;
                positions[i3 + 1] = y;
                positions[i3 + 2] = z;

                initialPos[i3] = x;
                initialPos[i3 + 1] = y;
                initialPos[i3 + 2] = z;

                sizes[i] = size;
                phases[i] = Math.random() * Math.PI * 2;
                radii[i] = radius;
                layers[i] = layer;
            }

            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('aInitialPos', new THREE.BufferAttribute(initialPos, 3));
            geometry.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));
            geometry.setAttribute('aPhase', new THREE.BufferAttribute(phases, 1));
            geometry.setAttribute('aRadius', new THREE.BufferAttribute(radii, 1));
            geometry.setAttribute('aLayer', new THREE.BufferAttribute(layers, 1));

            const theme = PALETTES[this.options.theme] || PALETTES.spectral;

            this.uniforms = {
                uTime: { value: 0.0 },
                uStateTime: { value: 0.0 },
                uAudioLevel: { value: 0.0 },
                uAudioBands: { value: new THREE.Vector3(0, 0, 0) },
                uState: { value: 0.0 },
                uStateTransition: { value: 1.0 },
                uPixelRatio: { value: this.renderer ? this.renderer.getPixelRatio() : 1.0 },
                uSizeMultiplier: { value: 1.0 },
                uBloomIntensity: { value: this.options.bloomIntensity },
                uColorCore: { value: theme.core.clone() },
                uColorInner: { value: theme.inner.clone() },
                uColorArms: { value: theme.arms.clone() },
                uColorOuter: { value: theme.outer.clone() },
                uColorSparks: { value: theme.sparks.clone() }
            };

            this.material = new THREE.ShaderMaterial({
                vertexShader: VERTEX_SHADER,
                fragmentShader: FRAGMENT_SHADER,
                uniforms: this.uniforms,
                transparent: true,
                depthWrite: false,
                blending: THREE.AdditiveBlending
            });

            this.particleSystem = new THREE.Points(geometry, this.material);
            this.scene.add(this.particleSystem);
        }

        _createGasLayers() {
            // Volumetric soft gas clouds layered along the galactic plane
            const gasGroup = new THREE.Group();
            const gasCanvas = document.createElement('canvas');
            gasCanvas.width = 128;
            gasCanvas.height = 128;
            const ctx = gasCanvas.getContext('2d');
            const grad = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
            grad.addColorStop(0.0, 'rgba(120, 80, 255, 0.35)');
            grad.addColorStop(0.4, 'rgba(40, 160, 255, 0.18)');
            grad.addColorStop(0.8, 'rgba(25, 10, 60, 0.06)');
            grad.addColorStop(1.0, 'rgba(0, 0, 0, 0)');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, 128, 128);

            const gasTexture = new THREE.CanvasTexture(gasCanvas);
            const gasMaterial = new THREE.MeshBasicMaterial({
                map: gasTexture,
                transparent: true,
                depthWrite: false,
                blending: THREE.AdditiveBlending,
                opacity: 0.45
            });

            const gasPlanes = [
                { scale: 3.2, y: 0.0, rot: 0.1 },
                { scale: 2.6, y: 0.12, rot: -0.2 },
                { scale: 2.2, y: -0.12, rot: 0.3 }
            ];

            gasPlanes.forEach(p => {
                const geom = new THREE.PlaneGeometry(p.scale, p.scale);
                const mesh = new THREE.Mesh(geom, gasMaterial.clone());
                mesh.rotation.x = -Math.PI * 0.42 + p.rot;
                mesh.position.y = p.y;
                gasGroup.add(mesh);
            });

            this.gasGroup = gasGroup;
            this.scene.add(gasGroup);
        }

        _createSpectrumRing() {
            // Fine circular spectrum ring (64 bars around the perimeter)
            const segments = 64;
            const geometry = new THREE.BufferGeometry();
            const positions = [];
            const angles = [];
            const heights = [];

            for (let i = 0; i <= segments; i++) {
                const a = (i / segments) * Math.PI * 2;
                // Bottom vertex
                positions.push(Math.cos(a) * 2.35, 0, Math.sin(a) * 2.35);
                angles.push(a);
                heights.push(0.0);
                // Top vertex
                positions.push(Math.cos(a) * 2.45, 0.15, Math.sin(a) * 2.45);
                angles.push(a);
                heights.push(1.0);
            }

            geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
            geometry.setAttribute('aAngle', new THREE.Float32BufferAttribute(angles, 1));
            geometry.setAttribute('aHeight', new THREE.Float32BufferAttribute(heights, 1));

            this.ringUniforms = {
                uTime: { value: 0.0 },
                uAudioLevel: { value: 0.0 },
                uBass: { value: 0.0 },
                uTreble: { value: 0.0 },
                uState: { value: 0.0 },
                uColor: { value: new THREE.Color(0x00f5ff) },
                uAlpha: { value: this.options.showSpectrumRing ? 0.75 : 0.0 }
            };

            const ringMat = new THREE.ShaderMaterial({
                vertexShader: RING_VERTEX_SHADER,
                fragmentShader: RING_FRAGMENT_SHADER,
                uniforms: this.ringUniforms,
                transparent: true,
                depthWrite: false,
                side: THREE.DoubleSide,
                blending: THREE.AdditiveBlending
            });

            this.spectrumRing = new THREE.Mesh(geometry, ringMat);
            this.spectrumRing.visible = this.options.showSpectrumRing;
            this.scene.add(this.spectrumRing);
        }

        _setupEvents() {
            // Visibility API: 0% CPU/GPU when window is minimized or hidden
            document.addEventListener('visibilitychange', () => {
                this.isPaused = document.hidden;
                if (!this.isPaused) {
                    this.clock.start();
                    requestAnimationFrame(this.animate);
                }
            });

            window.addEventListener('resize', () => {
                this.resize();
            });
        }

        _init2DFallback() {
            // Lightweight 2D canvas fallback if WebGL is unavailable
            const canvas = document.createElement('canvas');
            canvas.width = this.container.clientWidth || 300;
            canvas.height = this.container.clientHeight || 300;
            const ctx = canvas.getContext('2d');
            this.container.appendChild(canvas);

            let t = 0;
            const loop2D = () => {
                if (this.isPaused) return;
                t += 0.02;
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                const cx = canvas.width / 2;
                const cy = canvas.height / 2;
                const r = 60 + Math.sin(t * 2) * 6;
                const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
                grad.addColorStop(0, '#00f5ff');
                grad.addColorStop(0.5, '#b026ff');
                grad.addColorStop(1, 'transparent');
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(cx, cy, r, 0, Math.PI * 2);
                ctx.fill();
                requestAnimationFrame(loop2D);
            };
            requestAnimationFrame(loop2D);
        }

        // =====================================================================
        // PUBLIC CONTROL API
        // =====================================================================
        setState(state) {
            const stateMap = {
                'idle': 0.0,
                'listening': 1.0,
                'thinking': 2.0,
                'speaking': 3.0,
                'error': 4.0,
                'paused': 5.0
            };
            if (!(state in stateMap)) return;
            this.state = state;
            this.targetStateNum = stateMap[state];
            this.stateTransition = 0.0; // trigger transition

            // Update theme if special state
            if (state === 'error') {
                this._interpolateTheme(PALETTES.error);
                setTimeout(() => {
                    if (this.state === 'error') this.setState('idle');
                }, 900);
            } else if (state === 'paused') {
                this._interpolateTheme(PALETTES.paused);
            } else {
                this._interpolateTheme(PALETTES[this.currentThemeName] || PALETTES.spectral);
            }
        }

        setAudioLevel(level) {
            this.targetAudioLevel = Math.max(0.0, Math.min(1.0, Number(level) || 0.0));
        }

        setBands(bass, mid, treble) {
            this.audioBands.bass = Math.max(0.0, Math.min(1.0, Number(bass) || 0.0));
            this.audioBands.mid = Math.max(0.0, Math.min(1.0, Number(mid) || 0.0));
            this.audioBands.treble = Math.max(0.0, Math.min(1.0, Number(treble) || 0.0));
        }

        setTheme(themeName) {
            if (!(themeName in PALETTES)) themeName = 'spectral';
            this.currentThemeName = themeName;
            this._interpolateTheme(PALETTES[themeName]);
        }

        _interpolateTheme(targetPalette) {
            if (!this.uniforms) return;
            this.uniforms.uColorCore.value.copy(targetPalette.core);
            this.uniforms.uColorInner.value.copy(targetPalette.inner);
            this.uniforms.uColorArms.value.copy(targetPalette.arms);
            this.uniforms.uColorOuter.value.copy(targetPalette.outer);
            this.uniforms.uColorSparks.value.copy(targetPalette.sparks);
            if (this.ringUniforms) {
                this.ringUniforms.uColor.value.copy(targetPalette.core);
            }
        }

        setQuality(mode) {
            // Adaptive particle count scaler
            this.options.quality = mode;
            if (!this.particleSystem) return;

            let activeCount = this.options.particleCount;
            if (mode === 'low') activeCount = Math.min(35000, this.options.particleCount);
            else if (mode === 'medium') activeCount = Math.min(65000, this.options.particleCount);
            else if (mode === 'high') activeCount = this.options.particleCount;

            this.particleSystem.geometry.setDrawRange(0, activeCount);
        }

        setBloom(intensity) {
            this.options.bloomIntensity = Math.max(0.0, Math.min(2.5, Number(intensity) || 0.0));
            if (this.uniforms) {
                this.uniforms.uBloomIntensity.value = this.options.bloomIntensity;
            }
        }

        setSpeed(multiplier) {
            this.options.speedMultiplier = Math.max(0.1, Math.min(4.0, Number(multiplier) || 1.0));
        }

        toggleSpectrumRing(visible) {
            this.options.showSpectrumRing = !!visible;
            if (this.spectrumRing) {
                this.spectrumRing.visible = this.options.showSpectrumRing;
            }
        }

        resize() {
            if (!this.renderer || !this.camera) return;
            const w = this.container.clientWidth || 300;
            const h = this.container.clientHeight || 300;
            this.camera.aspect = w / h;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(w, h);
            if (this.uniforms) {
                this.uniforms.uPixelRatio.value = this.renderer.getPixelRatio();
            }
        }

        // =====================================================================
        // MAIN ANIMATION LOOP (60 FPS)
        // =====================================================================
        animate() {
            if (this.isPaused || !this.isRunning) return;

            requestAnimationFrame(this.animate);

            const delta = this.clock.getDelta();
            const elapsedTime = this.clock.getElapsedTime() * this.options.speedMultiplier;

            // 1. Audio smoothing (attack / release)
            const attackFactor = 0.35;
            const releaseFactor = 0.12;
            const factor = this.targetAudioLevel > this.audioLevel ? attackFactor : releaseFactor;
            this.audioLevel += (this.targetAudioLevel - this.audioLevel) * factor;

            // 2. State transition lerp (300-600ms)
            if (this.stateTransition < 1.0) {
                this.stateTransition = Math.min(1.0, this.stateTransition + delta * 2.8);
                this.stateNum += (this.targetStateNum - this.stateNum) * 0.22;
            } else {
                this.stateNum = this.targetStateNum;
            }

            // 3. Update uniforms
            if (this.uniforms) {
                this.uniforms.uTime.value = elapsedTime;
                this.uniforms.uAudioLevel.value = this.audioLevel;
                this.uniforms.uAudioBands.value.set(
                    this.audioBands.bass,
                    this.audioBands.mid,
                    this.audioBands.treble
                );
                this.uniforms.uState.value = this.stateNum;
                this.uniforms.uStateTransition.value = this.stateTransition;
            }

            if (this.ringUniforms) {
                this.ringUniforms.uTime.value = elapsedTime;
                this.ringUniforms.uAudioLevel.value = this.audioLevel;
                this.ringUniforms.uBass.value = this.audioBands.bass;
                this.ringUniforms.uTreble.value = this.audioBands.treble;
                this.ringUniforms.uState.value = this.stateNum;
            }

            // 4. Subtle camera parallax breathing
            if (this.camera) {
                this.camera.position.x = Math.sin(elapsedTime * 0.25) * 0.18;
                this.camera.position.y = 2.2 + Math.cos(elapsedTime * 0.35) * 0.12;
                this.camera.lookAt(0, 0, 0);
            }

            // 5. Rotate gas clouds slowly
            if (this.gasGroup) {
                this.gasGroup.rotation.y = elapsedTime * 0.08;
            }

            // 6. Adaptive Quality & FPS Monitoring
            this.frameCount++;
            const now = performance.now();
            if (now - this.lastFpsCheck >= 1000) {
                this.currentFps = Math.round((this.frameCount * 1000) / (now - this.lastFpsCheck));
                this.frameCount = 0;
                this.lastFpsCheck = now;

                if (this.options.onFpsUpdate) {
                    this.options.onFpsUpdate(this.currentFps);
                }

                // Auto throttle if fps < 45
                if (this.options.quality === 'auto' && this.particleSystem) {
                    if (this.currentFps < 45) {
                        const curRange = this.particleSystem.geometry.drawRange.count;
                        if (curRange > 35000) {
                            this.particleSystem.geometry.setDrawRange(0, Math.max(35000, curRange - 15000));
                        }
                    } else if (this.currentFps > 56) {
                        const curRange = this.particleSystem.geometry.drawRange.count;
                        if (curRange < this.options.particleCount) {
                            this.particleSystem.geometry.setDrawRange(0, Math.min(this.options.particleCount, curRange + 10000));
                        }
                    }
                }
            }

            this.renderer.render(this.scene, this.camera);
        }

        destroy() {
            this.isRunning = false;
            if (this.renderer && this.renderer.domElement) {
                this.renderer.dispose();
                this.renderer.domElement.remove();
            }
        }
    }

    return GalacticNebula;
}));
