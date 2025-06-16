import streamlit as st
import pandas as pd
from datetime import date
from utils.predict import train_model, predict_anomalies

st.set_page_config(page_title="Anomaly Detection Dashboard", layout="wide")
st.title("🔍 Splunk-Style Log Anomaly Detection Dashboard")

# Step 1: File uploader
uploaded_file = st.file_uploader("📤 Upload a CSV log file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, parse_dates=["timestamp"])
    st.subheader("📄 Raw Log Preview")
    st.dataframe(df.head())

    # Step 2: Run model
    with st.spinner("🧠 Training model and detecting anomalies..."):
        model = train_model(df)
        result = predict_anomalies(df, model)

    st.success("✅ Detection Complete")

    # Step 3: Filter only anomalies
    anomalies = result[result['anomaly'] == 'Anomaly'].copy()

    st.subheader(f"🚨 Detected {len(anomalies)} Anomalies")

    # ------------------ FILTERS ------------------ #
    st.markdown("### 🎯 Filter Results")

    # User filter
    users = anomalies['user'].dropna().unique().tolist()
    selected_user = st.selectbox("👤 Filter by User", ["All"] + users)
    if selected_user != "All":
        anomalies = anomalies[anomalies['user'] == selected_user]

    # IP filter
    search_ip = st.text_input("🌐 Search by IP (partial match)")
    if search_ip:
        anomalies = anomalies[anomalies['src_ip'].str.contains(search_ip, na=False)]

    # Action filter
    actions = anomalies['action'].dropna().unique().tolist()
    selected_actions = st.multiselect("⚙️ Filter by Action", actions, default=actions)
    anomalies = anomalies[anomalies['action'].isin(selected_actions)]

    # Time range filter (with NaT-safe slider)
    anomalies['timestamp'] = pd.to_datetime(anomalies['timestamp'], errors='coerce')
    anomalies = anomalies.dropna(subset=['timestamp'])

    if not anomalies.empty:
        min_date = anomalies['timestamp'].min().date()
        max_date = anomalies['timestamp'].max().date()

        if isinstance(min_date, date) and isinstance(max_date, date):
            date_range = st.slider(
                "🗓️ Filter by Date Range",
                min_value=min_date,
                max_value=max_date,
                value=(min_date, max_date)
            )
            anomalies = anomalies[
                (anomalies['timestamp'] >= pd.to_datetime(date_range[0])) &
                (anomalies['timestamp'] <= pd.to_datetime(date_range[1]))
            ]

    # ------------------ RESULTS TABLE ------------------ #
    st.subheader(f"📋 Filtered Anomalies ({len(anomalies)} found)")
    st.dataframe(anomalies)

    # ------------------ CHARTS ------------------ #
    st.markdown("### 📊 Visualizations")

    if not anomalies.empty:
        anomalies['hour'] = anomalies['timestamp'].dt.hour
        st.subheader("⏱ Anomalies by Hour")
        st.bar_chart(anomalies.groupby('hour').size())

        st.subheader("👤 Anomalies by User")
        st.bar_chart(anomalies['user'].value_counts())

        st.subheader("🌐 Anomalies by Top 10 IPs")
        st.bar_chart(anomalies['src_ip'].value_counts().head(10))

        st.subheader("⚙️ Anomalies by Action")
        st.bar_chart(anomalies['action'].value_counts())

    # ------------------ DOWNLOAD ------------------ #
    st.download_button(
        label="📥 Download Filtered Anomalies",
        data=anomalies.to_csv(index=False),
        file_name="anomalies_filtered.csv",
        mime="text/csv"
    )

else:
    st.info("Please upload a CSV file to begin.")
