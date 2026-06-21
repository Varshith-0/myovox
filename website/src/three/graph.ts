/**
 * A stylized node-graph for the NeuralNet layer: nodes scattered in a slab in
 * front of the head, edges to nearest neighbours, and pulse particles that
 * travel along those edges (animated in-shader via start/end/offset attributes).
 */

export interface Graph {
  nodes: Float32Array // 3 per node
  nodePhase: Float32Array // twinkle phase per node
  edgeLines: Float32Array // 6 per edge (segment endpoints) for LineSegments
  pulseStart: Float32Array // 3 per pulse (edge start)
  pulseEnd: Float32Array // 3 per pulse (edge end)
  pulseOffset: Float32Array // phase per pulse
  nodeCount: number
  pulseCount: number
}

export function buildGraph(nodeCount: number, neighbours = 2, pulsesPerEdge = 1): Graph {
  const nodes = new Float32Array(nodeCount * 3)
  const nodePhase = new Float32Array(nodeCount)
  for (let i = 0; i < nodeCount; i++) {
    nodes[i * 3] = (Math.random() * 2 - 1) * 2.0 // x
    nodes[i * 3 + 1] = -1.3 + Math.random() * 2.9 // y
    nodes[i * 3 + 2] = 0.6 + Math.random() * 2.4 // z (in front of head)
    nodePhase[i] = Math.random()
  }

  const dist2 = (a: number, b: number) => {
    const dx = nodes[a * 3] - nodes[b * 3]
    const dy = nodes[a * 3 + 1] - nodes[b * 3 + 1]
    const dz = nodes[a * 3 + 2] - nodes[b * 3 + 2]
    return dx * dx + dy * dy + dz * dz
  }

  // Unique edges via nearest-neighbour connection.
  const edgeSet = new Set<string>()
  const edges: [number, number][] = []
  for (let i = 0; i < nodeCount; i++) {
    const order = [...Array(nodeCount).keys()]
      .filter((j) => j !== i)
      .sort((a, b) => dist2(i, a) - dist2(i, b))
      .slice(0, neighbours)
    for (const j of order) {
      const key = i < j ? `${i}-${j}` : `${j}-${i}`
      if (!edgeSet.has(key)) {
        edgeSet.add(key)
        edges.push([i, j])
      }
    }
  }

  const edgeLines = new Float32Array(edges.length * 6)
  edges.forEach(([a, b], e) => {
    edgeLines[e * 6] = nodes[a * 3]
    edgeLines[e * 6 + 1] = nodes[a * 3 + 1]
    edgeLines[e * 6 + 2] = nodes[a * 3 + 2]
    edgeLines[e * 6 + 3] = nodes[b * 3]
    edgeLines[e * 6 + 4] = nodes[b * 3 + 1]
    edgeLines[e * 6 + 5] = nodes[b * 3 + 2]
  })

  const pulseCount = edges.length * pulsesPerEdge
  const pulseStart = new Float32Array(pulseCount * 3)
  const pulseEnd = new Float32Array(pulseCount * 3)
  const pulseOffset = new Float32Array(pulseCount)
  let p = 0
  for (const [a, b] of edges) {
    for (let k = 0; k < pulsesPerEdge; k++) {
      pulseStart[p * 3] = nodes[a * 3]
      pulseStart[p * 3 + 1] = nodes[a * 3 + 1]
      pulseStart[p * 3 + 2] = nodes[a * 3 + 2]
      pulseEnd[p * 3] = nodes[b * 3]
      pulseEnd[p * 3 + 1] = nodes[b * 3 + 1]
      pulseEnd[p * 3 + 2] = nodes[b * 3 + 2]
      pulseOffset[p] = Math.random()
      p++
    }
  }

  return {
    nodes,
    nodePhase,
    edgeLines,
    pulseStart,
    pulseEnd,
    pulseOffset,
    nodeCount,
    pulseCount,
  }
}
