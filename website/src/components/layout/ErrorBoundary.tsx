import { Component, type ReactNode } from 'react'
import { ErrorScreen, type ErrorVariant } from './ErrorScreen'
import { variantFor } from './chunkError'

/**
 * Top-level safety net. Without it, a render crash or a failed lazy-route chunk
 * unmounts the tree to a blank white screen. This catches both and shows a
 * brand-matched screen; the variant separates offline (retry) from a stale
 * deploy (reload). Recovery is a full reload, so no reset state is needed.
 */
export class ErrorBoundary extends Component<{ children: ReactNode }, { variant: ErrorVariant | null }> {
  state: { variant: ErrorVariant | null } = { variant: null }

  static getDerivedStateFromError(error: unknown) {
    return { variant: variantFor(error) }
  }

  render() {
    if (this.state.variant) return <ErrorScreen variant={this.state.variant} />
    return this.props.children
  }
}
