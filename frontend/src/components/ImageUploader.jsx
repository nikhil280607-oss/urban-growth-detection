import { useState, useRef } from "react";
import axios from "axios";

const API_URL = "http://localhost:8000";

export default function ImageUploader({ setResults, setLoading, setError, loading }) {
  const [beforeImage, setBeforeImage] = useState(null);
  const [afterImage, setAfterImage] = useState(null);
  const [beforePreview, setBeforePreview] = useState(null);
  const [afterPreview, setAfterPreview] = useState(null);
  const [useRay, setUseRay] = useState(false);

  const beforeRef = useRef();
  const afterRef = useRef();

  const handleImageSelect = (file, type) => {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      if (type === "before") {
        setBeforeImage(file);
        setBeforePreview(e.target.result);
      } else {
        setAfterImage(file);
        setAfterPreview(e.target.result);
      }
    };
    reader.readAsDataURL(file);
  };

  const handleDetect = async () => {
    if (!beforeImage || !afterImage) {
      setError("Please upload both Before and After images first.");
      return;
    }

    setError("");
    setLoading(true);
    setResults(null);

    const formData = new FormData();
    formData.append("before", beforeImage);
    formData.append("after", afterImage);

    try {
      // POST request to FastAPI backend (RESTful API call)
      const response = await axios.post(
        `${API_URL}/detect?use_ray=${useRay}`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      if (response.data.success) {
        const stats = response.data.data.statistics;

        // Call Gemini AI description endpoint
        try {
          const descResp = await axios.post(`${API_URL}/describe`, stats);
          response.data.data.ai_description = descResp.data.description;
        } catch {
          response.data.data.ai_description = "AI description unavailable.";
        }

        setResults(response.data.data);
      }
    } catch (err) {
      setError(
        err.response?.data?.detail || "Server error. Is the backend running?"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="uploader-section">
      <h2>Upload Satellite Images</h2>
      <p className="instruction">
        Upload two images of the same location taken at different times.
      </p>

      <div className="upload-grid">
        {/* Before Image */}
        <div className="upload-card" onClick={() => beforeRef.current.click()}>
          <input
            ref={beforeRef}
            type="file"
            accept="image/*"
            style={{ display: "none" }}
            onChange={(e) => handleImageSelect(e.target.files[0], "before")}
          />
          {beforePreview ? (
            <img src={beforePreview} alt="Before" className="preview-img" />
          ) : (
            <div className="upload-placeholder">
              <span>📷</span>
              <p>Click to upload BEFORE image</p>
              <small>Earlier year (e.g., 2015)</small>
            </div>
          )}
          <label className="upload-label">BEFORE</label>
        </div>

        {/* Arrow */}
        <div className="arrow-icon">→</div>

        {/* After Image */}
        <div className="upload-card" onClick={() => afterRef.current.click()}>
          <input
            ref={afterRef}
            type="file"
            accept="image/*"
            style={{ display: "none" }}
            onChange={(e) => handleImageSelect(e.target.files[0], "after")}
          />
          {afterPreview ? (
            <img src={afterPreview} alt="After" className="preview-img" />
          ) : (
            <div className="upload-placeholder">
              <span>🛰️</span>
              <p>Click to upload AFTER image</p>
              <small>Later year (e.g., 2024)</small>
            </div>
          )}
          <label className="upload-label">AFTER</label>
        </div>
      </div>

      <div className="options-row">
        <label className="toggle-label">
          <input
            type="checkbox"
            checked={useRay}
            onChange={(e) => setUseRay(e.target.checked)}
          />
          &nbsp; Use Ray Distributed Processing
        </label>
      </div>

      <button
        className="detect-btn"
        onClick={handleDetect}
        disabled={loading || !beforeImage || !afterImage}
      >
        {loading ? "⏳ Analyzing..." : "🔍 Detect Urban Changes"}
      </button>
    </div>
  );
}