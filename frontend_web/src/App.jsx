import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Bar, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import Settings from './pages/Settings'; // We will create this next
import './App.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

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
      <div className="nav-brand">🧪 ChemicalViz</div>
      <div className="nav-links">
        <Link to="/" className={`nav-btn ${isActive('/')}`}>Home</Link>
        <Link to="/settings" className={`nav-btn ${isActive('/settings')}`}>Settings</Link>
      </div>
    </nav>
  );
};

// --- Dashboard Component (Home) ---
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
      // --- CHANGE THIS LINE BACK TO FULL URL ---
      const response = await axios.post('http://127.0.0.1:8000/api/upload/', formData);
      
      setData(response.data.data);
    } catch (err) {
      console.error(err);
      setError("Failed to connect. Is Backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container fade-in">
      <h2 className="section-title">Upload Dataset</h2>
      
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
          {/* Stats Grid */}
          <div className="stats-grid">
            <div className="stat-box">
              <h3>Total Units</h3>
              <p>{data.total_count}</p>
            </div>
            <div className="stat-box">
              <h3>Avg Flow</h3>
              <p>{data.averages.avg_flowrate}</p>
            </div>
            <div className="stat-box">
              <h3>Avg Pressure</h3>
              <p>{data.averages.avg_pressure}</p>
            </div>
            <div className="stat-box">
              <h3>Avg Temp</h3>
              <p>{data.averages.avg_temperature}</p>
            </div>
          </div>

          {/* Charts */}
          <div className="charts-row">
            <div className="chart-container">
              <h3>Equipment Types</h3>
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
                  options={{ responsive: true, maintainAspectRatio: false }} 
                />
              </div>
            </div>
            
            <div className="chart-container">
              <h3>Metrics Overview</h3>
              <div className="chart-wrapper">
                <Bar 
                  data={{
                    labels: ['Flowrate', 'Pressure', 'Temperature'],
                    datasets: [{
                      label: 'Average',
                      data: [data.averages.avg_flowrate, data.averages.avg_pressure, data.averages.avg_temperature],
                      backgroundColor: ['#6366f1', '#f43f5e', '#eab308'],
                      borderRadius: 8,
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