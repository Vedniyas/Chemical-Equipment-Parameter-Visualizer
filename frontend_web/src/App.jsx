import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import { 
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement 
} from 'chart.js';
import { Bar, Pie, Line, Scatter } from 'react-chartjs-2';
import Settings from './pages/Settings';
import './App.css';

// Register all ChartJS components we need
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement);

// --- Navbar Component ---
const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);
  const isActive = (path) => location.pathname === path ? 'active-link' : '';
  return (
    <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
      <div className="nav-brand">🧪 ChemicalViz Pro</div>
      <div className="nav-links">
        <Link to="/" className={`nav-btn ${isActive('/')}`}>Dashboard</Link>
        <Link to="/settings" className={`nav-btn ${isActive('/settings')}`}>Settings</Link>
      </div>
    </nav>
  );
};

// --- New "Stat Card" Component for Professional Look ---
const StatCard = ({ title, data, unit }) => (
  <div className="stat-box professional-card">
    <div className="stat-header">
      <h3>{title}</h3>
      <span className="unit-badge">{unit}</span>
    </div>
    <div className="stat-main">
      <p className="stat-value">{data.avg}</p>
      <span className="stat-label">Average</span>
    </div>
    <div className="stat-footer">
      <div className="mini-stat">
        <span className="label">Min</span>
        <span className="value">{data.min}</span>
      </div>
      <div className="mini-stat">
        <span className="label">Max</span>
        <span className="value">{data.max}</span>
      </div>
      <div className="mini-stat">
        <span className="label">Median</span>
        <span className="value">{data.median}</span>
      </div>
    </div>
  </div>
);

// --- Dashboard Component ---
const Dashboard = () => {
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
      const response = await axios.post('http://127.0.0.1:8000/api/upload/', formData);
      setData(response.data.data);
    } catch (err) {
      console.error(err);
      setError("Failed to connect. Ensure Backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container fade-in">
      <h2 className="section-title">Process Analytics</h2>
      
      {/* Upload Section */}
      <div className="upload-hero">
        <div className="upload-box">
          <input type="file" onChange={handleFileChange} accept=".csv" />
          <button onClick={handleUpload} disabled={loading} className="cta-btn">
            {loading ? 'Analyzing Process Data...' : 'Start Analysis'}
          </button>
        </div>
        {error && <p className="error-text">{error}</p>}
      </div>

      {data && (
        <div className="dashboard-content">
          
          {/* 1. Key Performance Indicators (KPIs) */}
          <div className="kpi-grid">
            <StatCard title="Flowrate" data={data.stats.Flowrate} unit="L/min" />
            <StatCard title="Pressure" data={data.stats.Pressure} unit="PSI" />
            <StatCard title="Temperature" data={data.stats.Temperature} unit="°C" />
          </div>

          {/* 2. Advanced Visualizations Row */}
          <div className="charts-row">
            {/* Time Series Line Chart */}
            <div className="chart-container large">
              <h3>Process Stability (Time Series)</h3>
              <div className="chart-wrapper">
                <Line 
                  data={{
                    labels: data.chart_data.map((_, i) => i), // Simple index for x-axis
                    datasets: [
                      {
                        label: 'Pressure (PSI)',
                        data: data.chart_data.map(d => d.Pressure),
                        borderColor: '#f43f5e',
                        backgroundColor: 'rgba(244, 63, 94, 0.1)',
                        tension: 0.4, // Smooth curves
                        fill: true
                      },
                      {
                        label: 'Temperature (°C)',
                        data: data.chart_data.map(d => d.Temperature),
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                      }
                    ]
                  }} 
                  options={{ responsive: true, maintainAspectRatio: false, plugins: { title: { display: true, text: 'Pressure vs Temp Over Time' } } }} 
                />
              </div>
            </div>

            {/* Correlation Scatter Plot */}
            <div className="chart-container">
              <h3>Correlation Analysis</h3>
              <p className="chart-desc">Pressure vs. Flowrate Relationship</p>
              <div className="chart-wrapper">
                <Scatter 
                  data={{
                    datasets: [{
                      label: 'Samples',
                      data: data.chart_data.map(d => ({ x: d.Pressure, y: d.Flowrate })),
                      backgroundColor: '#6366f1',
                    }]
                  }}
                  options={{ 
                    responsive: true, 
                    maintainAspectRatio: false,
                    scales: {
                      x: { title: { display: true, text: 'Pressure (PSI)' } },
                      y: { title: { display: true, text: 'Flowrate (L/min)' } }
                    }
                  }}
                />
              </div>
            </div>
          </div>

          {/* 3. Distribution & Tables */}
          <div className="charts-row">
            <div className="chart-container">
              <h3>Equipment Distribution</h3>
              <div className="chart-wrapper">
                <Pie 
                  data={{
                    labels: Object.keys(data.distribution),
                    datasets: [{
                      data: Object.values(data.distribution),
                      backgroundColor: ['#6366f1', '#f43f5e', '#eab308', '#22c55e', '#14b8a6'],
                      borderWidth: 0
                    }]
                  }} 
                  options={{ responsive: true, maintainAspectRatio: false }} 
                />
              </div>
            </div>
          </div>

        </div>
      )}
    </div>
  );
};

function App() {
  return (
    <Router>
      <Navbar />
      <div className="main-wrapper">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;