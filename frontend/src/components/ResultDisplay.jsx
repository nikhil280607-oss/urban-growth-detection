export default function ResultDisplay({ results }) {
  const { statistics, change_map, heatmap, change_overlay, ai_description } = results;

  const severityColor = {
    Low: "#22c55e",
    Moderate: "#f59e0b",
    High: "#ef4444",
    Critical: "#7c3aed",
  };

  return (
    <div className="results-section">
      <h2>🔍 Change Detection Results</h2>

      {/* AI Description Box */}
      {ai_description && (
        <div className="ai-description">
          <h3>🤖 AI Analysis</h3>
          <p>{ai_description}</p>
        </div>
      )}

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-number">{statistics.change_percentage}%</span>
          <span className="stat-label">Area Changed</span>
        </div>
        <div className="stat-card">
          <span
            className="stat-number"
            style={{ color: severityColor[statistics.severity] }}
          >
            {statistics.severity}
          </span>
          <span className="stat-label">Severity Level</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">{statistics.num_change_clusters}</span>
          <span className="stat-label">Change Clusters</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">{statistics.avg_change_intensity}%</span>
          <span className="stat-label">Change Intensity</span>
        </div>
      </div>

      {/* Classification Banner */}
      <div
        className="classification-banner"
        style={{ borderColor: severityColor[statistics.severity] }}
      >
        <strong>Classification: </strong>
        {statistics.growth_classification}
      </div>

      {/* Visual Outputs */}
      <div className="visual-grid">
        <div className="visual-card">
          <h3>Change Map</h3>
          <p className="visual-desc">White = changed areas</p>
          <img src={change_map} alt="Change Map" />
        </div>
        <div className="visual-card">
          <h3>Heatmap</h3>
          <p className="visual-desc">Blue → Red = low → high change</p>
          <img src={heatmap} alt="Heatmap" />
        </div>
        <div className="visual-card">
          <h3>Change Overlay</h3>
          <p className="visual-desc">Red highlights = new urban growth</p>
          <img src={change_overlay} alt="Change Overlay" />
        </div>
      </div>
    </div>


    
  );

  {results.ml_classification_map && (
  <div className="visual-card">
    <h3>ML Classification Map</h3>
    <p className="visual-desc">🟢 No Change &nbsp; 🟡 Moderate &nbsp; 🔴 Urban Growth</p>
    <img src={results.ml_classification_map} alt="ML Classification" />
  </div>
)}
}