# splunk_fetch.py
import pandas as pd

def fetch_logs():
    df = pd.read_csv("Project\splunk\splunk-ai-anomaly\data\simulated_auth_logs.csv", parse_dates=["timestamp"])
    return df