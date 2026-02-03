import { useState, useEffect } from 'react';
import '../App.css';

const Settings = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [zoom, setZoom] = useState(100);

  // 1. Load saved settings on startup
  useEffect(() => {
    const saved = localStorage.getItem('chem_settings');
    if (saved) {
      const parsed = JSON.parse(saved);
      setDarkMode(parsed.darkMode || false);
      setZoom(parsed.zoom || 100);
    }
  }, []);

  // 2. Apply Dark Mode
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [darkMode]);

  // 3. Apply Zoom
  useEffect(() => {
    document.body.style.zoom = `${zoom}%`;
  }, [zoom]);

  // 4. Save Logic
  const saveSettings = () => {
    localStorage.setItem('chem_settings', JSON.stringify({ darkMode, zoom }));
    alert("Settings Saved!");
  };

  return (
    <div className="container fade-in">
      <h2 className="section-title">Preferences</h2>
      
      <div className="settings-panel">
        
        {/* Dark Mode Toggle */}
        <div className="setting-item">
          <div className="setting-info">
            <h3>Dark Mode</h3>
            <p>Switch between light and dark themes.</p>
          </div>
          <label className="switch">
            <input 
              type="checkbox" 
              checked={darkMode} 
              onChange={(e) => setDarkMode(e.target.checked)} 
            />
            <span className="slider round"></span>
          </label>
        </div>

        {/* Zoom Slider */}
        <div className="setting-item">
          <div className="setting-info">
            <h3>UI Zoom: {zoom}%</h3>
            <p>Adjust interface size.</p>
          </div>
          <input 
            type="range" 
            min="80" 
            max="150" 
            step="10"
            value={zoom} 
            onChange={(e) => setZoom(e.target.value)}
            className="zoom-slider"
          />
        </div>

        <button className="save-btn" onClick={saveSettings}>Save Changes</button>
      </div>
    </div>
  );
};

export default Settings;