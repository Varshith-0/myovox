import { memo } from 'react'
import { Canvas } from '@react-three/fiber'
import { useLocation } from 'react-router-dom'
import { HeadRig } from './HeadRig'
import { NeuralNet } from './NeuralNet'
import { Effects } from './Effects'
import { CameraRig } from './CameraRig'
import { SceneDriver } from './SceneDriver'
import { useStore } from '@/store/useStore'
import styles from './Scene.module.css'

/**
 * The fixed, full-viewport WebGL scene behind all content. Mounted once for the
 * whole app; it dims on the reading pages (Technical/Code) so text stays
 * legible, and runs the full choreography on the Story page. `pointer-events`
 * are off so it never intercepts scroll or clicks. Has an `aria-label` text
 * alternative describing the scene for assistive tech.
 */
export function Scene() {
  const { pathname } = useLocation()
  const isStory = pathname === '/'

  return (
    <div
      data-scene-root
      className={`${styles.scene} ${isStory ? '' : styles.dimmed}`}
      role="img"
      aria-label="A luminous white human head rendered as a cloud of points on a black field, transforming through the stages of decoding speech from facial-muscle signals."
    >
      <SceneCanvas />
    </div>
  )
}

/**
 * The WebGL canvas, isolated from route changes. The dim-on-reading-pages styling
 * above is just a CSS class on the wrapper, so navigation must NOT re-render the
 * Canvas: re-rendering the postprocessing EffectComposer throws on its circular
 * scene-graph refs ("Converting circular structure to JSON"), which trips the
 * SceneBoundary and loses the GL context (the whole scene vanishes). `memo` + no
 * `useLocation` here keeps it mounted and stable across navigation; it still
 * re-renders for genuine device changes (dpr / lowPower) via the store.
 */
const SceneCanvas = memo(function SceneCanvas() {
  const dpr = useStore((s) => s.dpr)
  const lowPower = useStore((s) => s.lowPower)

  return (
    <Canvas
      flat
      dpr={[1, dpr]}
      gl={{ antialias: !lowPower, powerPreference: 'high-performance', alpha: false }}
      camera={{ position: [0, 0.15, 4.4], fov: 38, near: 0.1, far: 100 }}
    >
      <color attach="background" args={['#050505']} />
      <SceneDriver />
      <CameraRig />
      <HeadRig />
      <NeuralNet />
      <Effects />
    </Canvas>
  )
})
