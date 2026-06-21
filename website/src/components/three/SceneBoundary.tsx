import { Component, type ReactNode } from 'react'
import { useStore } from '@/store/useStore'

interface Props {
  children: ReactNode
}
interface State {
  failed: boolean
}

/**
 * Guards the WebGL scene: if three.js / the GPU context fails (old device, no
 * WebGL, context loss), the app falls back to the black background and the
 * (fully readable) content instead of crashing — and dismisses the loader so
 * the page is usable. The brief's "degrade, don't crash" rule.
 */
export class SceneBoundary extends Component<Props, State> {
  state: State = { failed: false }

  static getDerivedStateFromError(): State {
    return { failed: true }
  }

  componentDidCatch() {
    useStore.getState().setReady(true)
  }

  render() {
    return this.state.failed ? null : this.props.children
  }
}
