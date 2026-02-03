import pandas as pd

def process_csv_data(file_path):
    try:
        df = pd.read_csv(file_path)
        # Clean column names
        df.columns = [c.strip() for c in df.columns]

        # 1. Total Count
        total_count = len(df)

        # 2. Averages
        stats = {}
        for col in ['Flowrate', 'Pressure', 'Temperature']:
            if col in df.columns:
                stats[f'avg_{col.lower()}'] = round(df[col].mean(), 2)
            else:
                stats[f'avg_{col.lower()}'] = 0

        # 3. Distribution
        if 'Type' in df.columns:
            distribution = df['Type'].value_counts().to_dict()
        else:
            distribution = {}

        return {
            "success": True,
            "total_count": total_count,
            "averages": stats,
            "distribution": distribution,
            "preview": df.head(10).to_dict(orient='records') 
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
