import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

def generate_report(ref_path='data/processed/test.csv', cur_path='data/processed/test.csv', out_html='monitoring/evidently_report.html'):
    ref = pd.read_csv(ref_path)
    cur = pd.read_csv(cur_path)
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=ref, current_data=cur)
    report.save_html(out_html)
    print(f"[evidently] saved report to {out_html}")

if __name__ == '__main__':
    generate_report()
