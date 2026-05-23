import { useState } from "react";
import ImageUploader from "./components/ImageUploader";
import ResultDisplay from "./components/ResultDisplay";
import "./App.css";

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🛰️ Urban Growth Detection System</h1>
        <p>Change Detection from Multi-Temporal Satellite Images</p>
        <p className="subtitle">AI212 Project — Remote Sensing & Geospatial Intelligence</p>
      </header>

      <main>
        <ImageUploader
          setResults={setResults}
          setLoading={setLoading}
          setError={setError}
          loading={loading}
        />

        {error && (
          <div className="error-box">
            ⚠️ {error}
          </div>
        )}

        {loading && (
          <div className="loading-box">
            <div className="spinner"></div>
            <p>Analyzing satellite images... Running change detection model...</p>
          </div>
        )}

        {results && !loading && (
          <ResultDisplay results={results} />
        )}
      </main>

      <footer>
        <p>Built with FastAPI · React · Docker · Ray · OpenCV</p>
      </footer>
    </div>
  );
}

export default App;