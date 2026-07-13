import os
import subprocess
import sys

def run_script(script_path):
    print("\n" + "=" * 60)
    print(f"RUNNING: {script_path}")
    print("=" * 60)
    
    # Run the script with python in a subprocess
    res = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    
    if res.returncode != 0:
        print(f"ERROR running {script_path}:")
        print(res.stderr)
        sys.exit(1)
    else:
        # Print stdout encoding safely for Windows console
        try:
            print(res.stdout)
        except UnicodeEncodeError:
            print(res.stdout.encode('ascii', errors='replace').decode('ascii'))

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define script sequence
    pipeline = [
        "src/utils/data_generator.py",
        "src/etl/profiling.py",
        "src/preprocessing/cleaner.py",
        "src/etl/star_schema_loader.py",
        "src/preprocessing/features.py",
        "src/segmentation/rfm.py",
        "src/segmentation/product_performance.py",
        "src/segmentation/cohort_analysis.py",
        "src/eda/visualizer.py",
        "src/fraud_detection/detector.py",
        "src/forecasting/forecaster.py",
        "src/utils/test_sql.py"
    ]
    
    for script in pipeline:
        full_path = os.path.join(base_dir, script)
        run_script(full_path)
        
    print("\n" + "=" * 60)
    print("ALL PIPELINE SCRIPTS EXECUTED SUCCESSFULLY!")
    print("=" * 60)
    
    # Verify outputs
    expected_outputs = [
        "data/raw/Master_Insurance_Data.xlsx",
        "data/processed/processed_insurance_data.csv",
        "data/processed/claims_analytics.db",
        "data/processed/customer_segments.csv",
        "data/processed/product_performance.csv",
        "data/processed/claims_forecast_90d.csv",
        "data/processed/cohort_pivot.csv",
        "reports/data_profiling_report.md",
        "reports/eda_report.md",
        "reports/product_performance_report.md",
        "reports/fraud_detection_report.md",
        "reports/forecast_report.md",
        "reports/cohort_report.md",
        "reports/technical_report.md",
        "documentation/er_diagram.md",
        "powerbi/powerbi_dashboard_spec.md",
        "images/customer_segments.png",
        "images/claims_forecast.png",
        "images/cohort_retention.png"
    ]
    
    print("\n--- VERIFYING ARTIFACT DELIVERABLES ---")
    missing_files = []
    for file in expected_outputs:
        file_path = os.path.join(base_dir, file)
        if os.path.exists(file_path):
            print(f"[OK] Found: {file}")
        else:
            print(f"[MISSING] File not found: {file}")
            missing_files.append(file)
            
    if not missing_files:
        print("\nSUCCESS: All deliverables verified and present!")
    else:
        print(f"\nFAILURE: {len(missing_files)} deliverables are missing.")
        sys.exit(1)

if __name__ == "__main__":
    main()
