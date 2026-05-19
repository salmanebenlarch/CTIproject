import type { EngineDetection } from '../types/analysis'

export function EngineResultsTable({ engines }: { engines: EngineDetection[] }) {
  return (
    <section className="card">
      <div className="section-header">
        <div>
          <p className="eyebrow">Scanner detail</p>
          <h3>Engine detections</h3>
        </div>
        <span className="counter-pill">{engines.length} engines</span>
      </div>
      {engines.length === 0 ? (
        <p className="muted-copy">No engine-level results were returned for this item.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Engine</th>
                <th>Category</th>
                <th>Result</th>
                <th>Method</th>
              </tr>
            </thead>
            <tbody>
              {engines.map((engine) => (
                <tr key={engine.engine_name}>
                  <td>{engine.engine_name}</td>
                  <td>{engine.category ?? '-'}</td>
                  <td>{engine.result ?? '-'}</td>
                  <td>{engine.method ?? '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
