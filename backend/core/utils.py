import pandas as pd
import numpy as np

def process_csv_data(file_path):
    try:
        # 1. Load Data
        df = pd.read_csv(file_path)
        # Clean headers: " Flowrate " -> "Flowrate"
        df.columns = [c.strip().title() for c in df.columns]

        # 2. Validation
        required_cols = ['Flowrate', 'Pressure', 'Temperature']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            return {"success": False, "error": f"Missing columns: {', '.join(missing)}"}

        # 3. Handle Time Series
        time_col = next((col for col in df.columns if col in ['Time', 'Timestamp', 'Date', 'Hour']), None)
        if time_col:
            df.sort_values(by=time_col, inplace=True)
            # Downsample for charts (take 1 point every 10 rows to prevent lag)
            chart_data = df.iloc[::10].to_dict(orient='records')
        else:
            # If no time, just create a dummy index for plotting
            df['Index'] = range(1, len(df) + 1)
            chart_data = df.iloc[::10].to_dict(orient='records')
            time_col = 'Index'

        # 4. Advanced Statistics Calculation
        stats = {}
        for col in required_cols:
            stats[col] = {
                'avg': round(df[col].mean(), 2),
                'std': round(df[col].std(), 2),
                'min': round(df[col].min(), 2),
                'max': round(df[col].max(), 2),
                'median': round(df[col].median(), 2)
            }

        # 5. Correlation Analysis (Professional Feature)
        # Calculates how much Flowrate and Pressure affect each other (-1 to 1)
        correlation_matrix = df[required_cols].corr().round(2).to_dict()

        # 6. Anomaly Detection (Safety Check)
        # "Critical" if value is > Mean + 2 Standard Deviations
        pressure_limit = stats['Pressure']['avg'] + (2 * stats['Pressure']['std'])
        anomalies = df[df['Pressure'] > pressure_limit]
        anomaly_count = len(anomalies)

        # 7. Distribution for Pie Chart
        if 'Type' in df.columns:
            distribution = df['Type'].value_counts().to_dict()
        else:
            distribution = {}

        return {
            "success": True,
            "total_count": len(df),
            "stats": stats,                  # NEW: Detailed stats
            "correlation": correlation_matrix, # NEW: Correlations
            "distribution": distribution,
            "preview": df.head(5).replace({np.nan: None}).to_dict(orient='records'),
            "anomaly_count": anomaly_count,
            "chart_data": chart_data,        # NEW: For Line/Scatter charts
            "time_col": time_col
        }

    except Exception as e:
        return {"success": False, "error": str(e)}