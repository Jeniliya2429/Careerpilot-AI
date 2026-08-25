import React from 'react'

export function SkeletonLine({ width = '100%', height = 14 }) {
  return <div className="skeleton" style={{ width, height, borderRadius: 6 }} />
}

export function SkeletonBlock({ height = 120 }) {
  return <div className="skeleton" style={{ width: '100%', height, borderRadius: 12 }} />
}

export function SkeletonCard() {
  return (
    <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <SkeletonLine width="40%" height={12} />
      <SkeletonLine width="90%" />
      <SkeletonLine width="75%" />
    </div>
  )
}
