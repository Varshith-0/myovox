/**
 * Loader for the occluder mesh baked alongside the point cloud
 * (`public/head-mesh.bin`): a compact binary of
 * `[u32 vertCount][u32 indexCount][f32 positions…][u32 indices…]`, already in
 * the same centered/scaled space as the points. Rendered as a black solid just
 * inside the cloud so the back-facing points are hidden and the head reads as a
 * rim-lit silhouette instead of a translucent blob.
 */

export interface HeadMesh {
  positions: Float32Array
  indices: Uint32Array
}

export async function loadHeadMesh(url: string): Promise<HeadMesh | null> {
  try {
    const res = await fetch(url)
    if (!res.ok) return null
    const buf = await res.arrayBuffer()
    const header = new Uint32Array(buf, 0, 2)
    const vertCount = header[0]
    const indexCount = header[1]
    if (!vertCount || !indexCount) return null
    const positions = new Float32Array(buf, 8, vertCount * 3)
    const indices = new Uint32Array(buf, 8 + vertCount * 3 * 4, indexCount)
    return { positions, indices }
  } catch {
    return null
  }
}
