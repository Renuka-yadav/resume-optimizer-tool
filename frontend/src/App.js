import React, { useState } from 'react';
import './App.css';

function App() {
  const [jd, setJd] = useState('');
  const [resume, setResume] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDownload = async (format) => {
    if (!analysisResult || !analysisResult.recruiterSummary) return;

    try {
      const response = await fetch(`http://127.0.0.1:5000/download/${format}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: analysisResult.recruiterSummary }),
      });
      
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Optimized_Resume.${format}`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

    } catch (error) {
      console.error("Error downloading file:", error);
      setError(`Failed to download ${format} file.`);
    }
  };

  const handleAnalyze = async () => {
    if (!jd || !resume) {
      setError("Please provide both a job description and a resume file.");
      return;
    }
    setIsLoading(true);
    setAnalysisResult(null);
    setError('');

    try {
      const response = await fetch('http://127.0.0.1:5000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_id: 1, job_id: 1 }), // Using seeded data for now
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({})); // Catch cases where response is not JSON
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setAnalysisResult(data.jobFitAnalysis);

    } catch (error) {
      console.error("Error fetching analysis:", error);
      setError("Failed to get analysis. Please ensure your backend server is running and check its terminal for errors.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>🚀 AI Resume Optimizer</h1>
          <p>Get your resume ready for top companies.</p>
        </div>
      </header>
      <main className="container">
        <div className="main-content">
          <div className="input-form">
            <h2>1. Provide the Details</h2>
            <textarea
              className="jd-textarea"
              placeholder="Paste the entire Job Description here..."
              value={jd}
              onChange={(e) => setJd(e.target.value)}
            />
            <label htmlFor="file-upload" className="custom-file-upload">
              {resume ? resume.name : 'Upload Your Resume'}
            </label>
            <input id="file-upload" type="file" onChange={(e) => setResume(e.target.files[0])} />
            <button onClick={handleAnalyze} disabled={isLoading}>
              {isLoading ? 'Analyzing...' : 'Analyze My Resume'}
            </button>
          </div>

          <div className="results-display">
            <h2>2. Get Your Results</h2>
            {isLoading && <div className="spinner"></div>}
            {error && <div className="error-message">{error}</div>}
            {analysisResult && (
              <div className="results-container">
                <div className="score-widget">
                  <div className="score-label">Match Score</div>
                  <div className="score-value">{analysisResult.matchScore}%</div>
                </div>
                <div className="download-widget">
                  <h3>Download Optimized Resume</h3>
                  <div className="download-buttons">
                    <button onClick={() => handleDownload('pdf')}>PDF</button>
                    <button onClick={() => handleDownload('docx')}>DOCX</button>
                    <button onClick={() => handleDownload('txt')}>TXT</button>
                  </div>
                </div>
                <div className="preview-widget">
                  <h3>Optimized Resume Preview</h3>
                  <pre className="resume-preview">{analysisResult.recruiterSummary}</pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;