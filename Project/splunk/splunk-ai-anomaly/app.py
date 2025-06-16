from splunk_fetch import fetch_logs
from utils.predict import train_model, predict_anomalies

def main():
    print ("Fetching logs")
    df = fetch_logs()
    print(f"✅ Loaded {len(df)} total log entries.")

    print("Training model...")
    model = train_model(df)

    print("Predicting anomalies...")
    result = predict_anomalies(df, model)

    # 🔎 Show ALL anomalies
    anomalies = result[result['anomaly'] == 'Anomaly']
    if anomalies.empty:
        print("✅ No anomalies detected.")
    else:
        print("🚨 Anomalies Detected:")
        print(anomalies[['timestamp', 'user', 'src_ip', 'action', 'host', 'anomaly']].to_string(index=False))

        # Optional: Save to CSV
        anomalies.to_csv("data/detected_anomalies.csv", index=False)
        print("\n💾 Saved anomalies to data/detected_anomalies.csv")

if __name__ == '__main__':
    main()