/**
 * The homepage's single continuous shot: one GPU particle system whose targets
 * morph between formations (dust → currents → cathedral → waves → a point →
 * the logotype) as scroll progress advances. All motion lives in the vertex
 * shader; the CPU only updates a handful of uniforms per frame.
 *
 * Glow comes from additive soft sprites — no post-processing chain needed.
 * ponytail: no bloom/DoF/motion-blur passes; add EffectComposer only if the
 * sprite glow measurably falls short on desktop.
 */
import {
  AdditiveBlending,
  BufferAttribute,
  BufferGeometry,
  MathUtils,
  PerspectiveCamera,
  Points,
  Scene,
  ShaderMaterial,
  Vector3,
  WebGLRenderer,
} from 'three'
import {
  FOCUS,
  POINT,
  buildCathedral,
  buildDust,
  buildLogo,
  buildStreams,
  buildWave,
} from './formations'

/** Scroll keyframes: at progress `p` the swarm should hold formation `f`. */
const TRACK = [
  { p: 0.0, f: 0 }, // dust
  { p: 0.14, f: 0 },
  { p: 0.28, f: 1 }, // currents
  { p: 0.37, f: 1 },
  { p: 0.5, f: 2 }, // cathedral
  { p: 0.63, f: 2 },
  { p: 0.73, f: 3 }, // waves
  { p: 0.78, f: 3 },
  { p: 0.875, f: 4 }, // convergence
  { p: 0.905, f: 4 }, // the silence
  { p: 0.955, f: 5 }, // the reveal
  { p: 1.001, f: 5 },
] as const

/** Idle breathing amplitude per formation (structured forms stay crisp). */
const DRIFT = [0.26, 0.1, 0.09, 0.08, 0.04, 0.04]

interface Morph {
  from: number
  to: number
  blend: number
}

function morphAt(progress: number): Morph {
  for (let i = 0; i < TRACK.length - 1; i++) {
    const a = TRACK[i]
    const b = TRACK[i + 1]
    if (progress < b.p) {
      const span = b.p - a.p
      return { from: a.f, to: b.f, blend: span > 0 ? (progress - a.p) / span : 1 }
    }
  }
  return { from: 5, to: 5, blend: 1 }
}

/** Per-transition character: how violently the swarm travels between forms. */
function transitionFeel(from: number, to: number, blend: number) {
  if (from === to) {
    // Holding a formation: no travel energy, only the idle breathing.
    return { spiral: 0, swirlAmp: 0, stagger: 0.45, blend: 1 }
  }
  if (from === POINT && to === 5) {
    // The explosion: tight, fast, radial.
    return { spiral: -1.2, swirlAmp: 1.2, stagger: 0.12, blend: 1 - (1 - blend) ** 4 }
  }
  if (to === POINT) {
    // The collapse: accelerating inward spiral.
    return { spiral: 3.2, swirlAmp: 4.5, stagger: 0.5, blend: blend ** 2 }
  }
  return { spiral: 0.4, swirlAmp: 2.4, stagger: 0.45, blend }
}

/** Camera resting depth — the logo forms 56 units ahead of it. */
const CAM_REST_Z = -206
const FOV = 50

function cameraZ(progress: number): number {
  const approach = MathUtils.smoothstep(progress, 0, 0.37)
  const flight = MathUtils.smoothstep(progress, 0.37, 0.875)
  return 34 - 14 * approach + (CAM_REST_Z - 20) * flight
}

const VERTEX = /* glsl */ `
  attribute vec3 aStreams;
  attribute vec3 aCath;
  attribute vec3 aWave;
  attribute vec3 aLogo;
  attribute float aSeed;

  uniform float uFrom;
  uniform float uTo;
  uniform float uBlend;
  uniform float uStagger;
  uniform float uSpiral;
  uniform float uSwirlAmp;
  uniform float uDrift;
  uniform float uCondense;
  uniform float uTurb;
  uniform float uTime;
  uniform float uFade;
  uniform float uSize;
  uniform float uEnd;
  uniform float uLogoScale;
  uniform vec3 uFocus;

  varying float vAlpha;

  vec3 formation(float f) {
    if (f < 0.5) return position;
    if (f < 1.5) return aStreams;
    if (f < 2.5) return aCath;
    if (f < 3.5) return aWave;
    if (f < 4.5) return uFocus
      + normalize(vec3(sin(aSeed * 783.0), cos(aSeed * 347.0), sin(aSeed * 519.0)))
      * (0.1 + 0.8 * aSeed * aSeed);
    return uFocus + aLogo * uLogoScale;
  }

  void main() {
    // Per-particle staggered blend so the swarm morphs as a murmuration,
    // never as one rigid tween.
    float k = clamp((uBlend - aSeed * uStagger) / max(1e-4, 1.0 - uStagger), 0.0, 1.0);
    k = k * k * (3.0 - 2.0 * k);

    vec3 p = mix(formation(uFrom), formation(uTo), k);

    // Mid-morph energy: spiral around the story axis + curl-ish drift.
    float sw = k * (1.0 - k) * 4.0;
    float ang = sw * uSpiral * (0.4 + aSeed);
    vec2 rel = p.xy - uFocus.xy;
    p.xy = uFocus.xy + vec2(rel.x * cos(ang) - rel.y * sin(ang), rel.x * sin(ang) + rel.y * cos(ang));
    p += sw * uSwirlAmp * vec3(
      sin(aSeed * 91.0 + uTime * 0.7 + p.z * 0.2),
      cos(aSeed * 57.0 + uTime * 0.6 + p.x * 0.2),
      sin(aSeed * 73.0 + uTime * 0.5)
    );

    // Everything breathes, always.
    p += uDrift * (0.4 + 0.6 * fract(aSeed * 7.0)) * vec3(
      sin(uTime * 0.5 + aSeed * 37.0),
      sin(uTime * 0.42 + aSeed * 61.0),
      sin(uTime * 0.55 + aSeed * 83.0)
    );

    // Scroll gestures ripple through the swarm.
    p += uTurb * aSeed * vec3(
      sin(aSeed * 641.0 + uTime * 7.0),
      cos(aSeed * 277.0 + uTime * 6.0),
      sin(aSeed * 431.0 + uTime * 8.0)
    );

    vec4 mv = modelViewMatrix * vec4(p, 1.0);
    float dist = max(-mv.z, 0.001);

    float brightness = 0.45 + 0.55 * fract(aSeed * 13.7);
    vAlpha = brightness * uFade
      * smoothstep(240.0, 60.0, dist)   // depth haze
      * smoothstep(0.6, 6.0, dist)      // don't blow out at the lens
      * mix(1.0, 0.07, uCondense)       // dim during full convergence
      * (1.0 - 0.8 * uEnd);             // recede as the crisp logotype takes over

    gl_PointSize = clamp(uSize * (0.5 + aSeed) * (150.0 / dist) * mix(1.0, 0.3, uCondense), 0.5, 40.0);
    gl_Position = projectionMatrix * mv;
  }
`

const FRAGMENT = /* glsl */ `
  precision mediump float;
  varying float vAlpha;

  void main() {
    float d = length(gl_PointCoord - 0.5) * 2.0;
    float core = exp(-d * d * 28.0) * 0.65;
    float halo = exp(-d * d * 7.0) * 0.35;
    gl_FragColor = vec4(vec3(0.961, 0.957, 0.945), (core + halo) * vAlpha);
  }
`

export interface Quality {
  count: number
  dpr: number
}

export class HomeScene {
  private renderer: WebGLRenderer
  private scene = new Scene()
  private camera: PerspectiveCamera
  private material: ShaderMaterial
  private geometry: BufferGeometry
  private time = 0
  private turbulence = 0
  private lastProgress = 0
  private parallax = { x: 0, y: 0 }
  private lookTarget = new Vector3()

  private constructor(canvas: HTMLCanvasElement, quality: Quality, logo: { points: Float32Array }) {
    this.renderer = new WebGLRenderer({
      canvas,
      antialias: false,
      powerPreference: 'high-performance',
    })
    this.renderer.setClearColor(0x000000, 1)
    this.renderer.setPixelRatio(quality.dpr)

    this.camera = new PerspectiveCamera(FOV, 1, 0.1, 400)

    const n = quality.count
    const seeds = new Float32Array(n)
    for (let i = 0; i < n; i++) seeds[i] = Math.random()

    this.geometry = new BufferGeometry()
    this.geometry.setAttribute('position', new BufferAttribute(buildDust(n), 3))
    this.geometry.setAttribute('aStreams', new BufferAttribute(buildStreams(n), 3))
    this.geometry.setAttribute('aCath', new BufferAttribute(buildCathedral(n), 3))
    this.geometry.setAttribute('aWave', new BufferAttribute(buildWave(n), 3))
    this.geometry.setAttribute('aLogo', new BufferAttribute(logo.points, 3))
    this.geometry.setAttribute('aSeed', new BufferAttribute(seeds, 1))

    this.material = new ShaderMaterial({
      vertexShader: VERTEX,
      fragmentShader: FRAGMENT,
      transparent: true,
      depthTest: false,
      depthWrite: false,
      blending: AdditiveBlending,
      uniforms: {
        uFrom: { value: 0 },
        uTo: { value: 0 },
        uBlend: { value: 0 },
        uStagger: { value: 0.45 },
        uSpiral: { value: 0.4 },
        uSwirlAmp: { value: 2.4 },
        uDrift: { value: DRIFT[0] },
        uCondense: { value: 0 },
        uTurb: { value: 0 },
        uTime: { value: 0 },
        uFade: { value: 0 },
        uSize: { value: 2.0 * quality.dpr },
        uEnd: { value: 0 },
        uLogoScale: { value: 40 },
        uFocus: { value: new Vector3(FOCUS.x, FOCUS.y, FOCUS.z) },
      },
    })

    const points = new Points(this.geometry, this.material)
    // Positions are computed in the vertex shader; the CPU-side bounds (the
    // dust formation) mean nothing once the camera flies past them.
    points.frustumCulled = false
    this.scene.add(points)
  }

  /** Async because the logotype is sampled from rasterized text (font load). */
  static async create(canvas: HTMLCanvasElement, quality: Quality): Promise<HomeScene> {
    const logo = await buildLogo(quality.count)
    return new HomeScene(canvas, quality, logo)
  }

  setParallax(x: number, y: number): void {
    this.parallax.x = x
    this.parallax.y = y
  }

  resize(width: number, height: number): void {
    this.renderer.setSize(width, height, false)
    this.camera.aspect = width / height
    this.camera.updateProjectionMatrix()

    // Size the logotype to the viewport seen from the camera's resting spot.
    const distance = Math.abs(FOCUS.z - CAM_REST_Z)
    const visibleH = 2 * distance * Math.tan(MathUtils.degToRad(FOV / 2))
    const visibleW = visibleH * this.camera.aspect
    // 0.6 of the visible width matches the DOM logotype it crossfades into.
    this.material.uniforms.uLogoScale.value = Math.min(visibleW * 0.6, (visibleH * 0.5) / 0.22)
  }

  frame(progress: number, dt: number): void {
    this.time += dt
    const u = this.material.uniforms

    const morph = morphAt(progress)
    const feel = transitionFeel(morph.from, morph.to, morph.blend)
    u.uFrom.value = morph.from
    u.uTo.value = morph.to
    u.uBlend.value = feel.blend
    u.uStagger.value = feel.stagger
    u.uSpiral.value = feel.spiral
    u.uSwirlAmp.value = feel.swirlAmp
    u.uDrift.value = MathUtils.lerp(DRIFT[morph.from], DRIFT[morph.to], feel.blend)

    const condense = (f: number) => (f === POINT ? 1 : 0)
    u.uCondense.value = MathUtils.lerp(condense(morph.from), condense(morph.to), feel.blend)

    // Scroll velocity → a decaying ripple through the swarm.
    const velocity = Math.abs(progress - this.lastProgress) / Math.max(dt, 1e-4)
    this.lastProgress = progress
    this.turbulence = MathUtils.lerp(
      this.turbulence,
      Math.min(velocity * 14, 1),
      1 - Math.exp(-3 * dt),
    )
    u.uTurb.value = this.turbulence * 1.1

    u.uEnd.value = MathUtils.smoothstep(progress, 0.975, 1)
    u.uTime.value = this.time
    // Motes surface out of darkness over the first seconds, before any scroll.
    u.uFade.value = MathUtils.smoothstep(this.time, 0.8, 4.5)

    // Camera: one long, easing flight; the world stills as it arrives.
    const z = cameraZ(progress)
    const flight = MathUtils.smoothstep(progress, 0.37, 0.875)
    const settle = 1 - MathUtils.smoothstep(progress, 0.78, 0.9) // sway dies before the silence
    const sway = Math.sin(progress * 7.2) * 1.8 * flight * settle
    const bob = Math.sin(progress * 5.1) * 0.8 * flight * settle
    this.camera.position.set(sway + this.parallax.x * 1.4, 2 + bob + this.parallax.y * 0.9, z)
    this.lookTarget.set(sway * 0.3 + this.parallax.x * 0.5, 2 + this.parallax.y * 0.3, z - 60)
    this.camera.lookAt(this.lookTarget)

    this.renderer.render(this.scene, this.camera)
  }

  dispose(): void {
    this.geometry.dispose()
    this.material.dispose()
    this.renderer.dispose()
  }
}
