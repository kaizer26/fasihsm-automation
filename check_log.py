import pandas as pd
import os

log_file = r"d:\2026\SCRAPING\FASIH-SM\backend\output\log\Log_Approve_TANAH BUMBU_IMK Tahunan 2025 - Pencacahan_Pencacahan_20260114_210614.xlsx"

if os.path.exists(log_file):
    df = pd.read_excel(log_file)
    print("Columns:", df.columns.tolist())
    if 'status' in df.columns:
        print("Unique Statuses:", df['status'].unique().tolist())
    if 'role' in df.columns:
        print("Unique Roles:", df['role'].unique().tolist())
    
    # Also check result and message
    if 'result' in df.columns:
        print("Results:", df['result'].value_counts().to_dict())
else:
    print("File not found")
