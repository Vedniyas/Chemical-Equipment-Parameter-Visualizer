import { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import './App.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

// --- 1. NEW NAVBAR COMPONENT ---
const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      // If user scrolls down more than 20px, enable "scrolled" mode
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
      <div className="nav-brand">🧪 ChemicalViz</div>
      <div className="nav-links">
        <button className="nav-btn">Dashboard</button>
        <button className="nav-btn">History</button>
        <button className="nav-btn">Settings</button>
      </div>
    </nav>
  );
};

function App() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleUpload = async () => {
    if (!file) { alert("Please select a file first!"); return; }
    const formData = new FormData();
    formData.append('file', file);
    setLoading(true); setError(null);

    try {
      // --- 2. UPDATED URL TO LOCALHOST ---
      // NOTE: Make sure your Django backend is running on port 8000
      const response = await axios.post('http://127.0.0.1:8000/api/upload/', formData);
      setData(response.data.data);
    } catch (err) {
      console.error(err);
      setError("Failed to connect to the server. Is the Backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      
      {/* Added a main-wrapper to push content below the fixed navbar */}
      <div className="main-wrapper">
        <div className="container">
          <h2 className="section-title">Upload Dataset</h2>

          {/* Hero Upload Section */}
          <div className="upload-hero">
            <div className="upload-box">
              <input type="file" onChange={handleFileChange} accept=".csv" />
              <button onClick={handleUpload} disabled={loading}>
                {loading ? 'Processing...' : 'Analyze Dataset'}
              </button>
            </div>
            {error && <p className="error-text">{error}</p>}
          </div>

          {data && (
            <div className="dashboard-content">
              
              {/* Stats Row */}
              <div className="stats-grid">
                <div className="stat-box">
                  <h3>Equipment Count</h3>
                  <p>{data.total_count}</p>
                </div>
                <div className="stat-box">
                  <h3>Avg Flowrate</h3>
                  <p>{data.averages.avg_flowrate}</p>
                  {/* Shows Standard Deviation if available from backend */}
                  {data.averages.std_flowrate && <small className="stat-sub">±{data.averages.std_flowrate}</small>}
                </div>
                <div className="stat-box">
                  <h3>Avg Pressure</h3>
                  <p>{data.averages.avg_pressure}</p>
                  {data.averages.std_pressure && <small className="stat-sub">±{data.averages.std_pressure}</small>}
                </div>
                <div className="stat-box">
                  <h3>Avg Temp</h3>
                  <p>{data.averages.avg_temperature}</p>
                  {data.averages.std_temperature && <small className="stat-sub">±{data.averages.std_temperature}</small>}
                </div>
              </div>

              {/* Charts Row */}
              <div className="charts-row">
                <div className="chart-container">
                  <h3>Type Distribution</h3>
                  <div className="chart-wrapper">
                    <Pie 
                      data={{
                        labels: Object.keys(data.distribution),
                        datasets: [{
                          data: Object.values(data.distribution),
                          backgroundColor: ['#6366f1', '#f43f5e', '#eab308', '#22c55e', '#3b82f6'],
                          borderWidth: 0
                        }]
                      }} 
                      options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { boxWidth: 12 } } } }} 
                    />
                  </div>
                </div>
                
                <div className="chart-container">
                  <h3>Performance Metrics</h3>
                  <div className="chart-wrapper">
                    <Bar 
                      data={{
                        labels: ['Flowrate', 'Pressure', 'Temperature'],
                        datasets: [{
                          label: 'Average Value',
                          data: [data.averages.avg_flowrate, data.averages.avg_pressure, data.averages.avg_temperature],
                          backgroundColor: ['#6366f1', '#f43f5e', '#eab308'],
                          borderRadius: 8,
                          barThickness: 60,
                        }]
                      }} 
                      options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { borderDash: [5, 5] } } } }} 
                    />
                  </div>
                </div>
              </div>

              {/* Table */}
              <div className="table-wrapper">
                <div className="table-scroll">
                   <h3>Raw Data Preview</h3>
                   <table>
                      <thead>
                        <tr>
                          {Object.keys(data.preview[0] || {}).map((key) => <th key={key}>{key}</th>)}
                        </tr>
                      </thead>
                      <tbody>
                        {data.preview.map((row, i) => (
                          <tr key={i}>
                            {Object.values(row).map((val, j) => <td key={j}>{val}</td>)}
                          </tr>
                        ))}
                      </tbody>
                   </table>
                </div>
              </div>

            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default App;