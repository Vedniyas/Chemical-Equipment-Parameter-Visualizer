# core/utils.py
import pandas as pd

def process_csv_data(file_path):
    """
    Reads CSV and calculates stats required:
    - Total count
    - Averages (Flowrate, Pressure, Temperature)
    - Equipment Type Distribution
    """
    try:
        df = pd.read_csv(file_path)

        # Standardizing column names to avoid KeyErrors (strip spaces, lowercase)
        df.columns = [c.strip() for c in df.columns]

        # 1. Total Count [cite: 14]
        total_count = len(df)

        # 2. Averages [cite: 14]
        # We verify if columns exist to prevent crashes
        stats = {}
        for col in ['Flowrate', 'Pressure', 'Temperature']:
            if col in df.columns:
                stats[f'avg_{col.lower()}'] = round(df[col].mean(), 2)
            else:
                stats[f'avg_{col.lower()}'] = 0

        # 3. Type Distribution [cite: 14]
        if 'Type' in df.columns:
            distribution = df['Type'].value_counts().to_dict()
        else:
            distribution = {}

        return {
            "success": True,
            "total_count": total_count,
            "averages": stats,
            "distribution": distribution,
            # We return the first few rows to display the table in frontend
            "preview": df.head(10).to_dict(orient='records') 
        }

    except Exception as e:
        return {"success": False, "error": str(e)}