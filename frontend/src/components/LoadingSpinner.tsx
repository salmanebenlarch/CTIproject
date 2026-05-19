export function LoadingSpinner({ label = 'Loading...' }: { label?: string }) {
  return <div className="loading">{label}</div>
}
