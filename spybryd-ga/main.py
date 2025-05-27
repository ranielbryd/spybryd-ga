from fastapi.responses import JSONResponse
from fastapi import FastAPI
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric
from google.oauth2 import service_account

app = FastAPI()

KEY_PATH = "spybryd-3ef808c31aa4.json"
PROPERTY_ID = "376255082"

@app.get("/ga/overview")
def get_analytics_overview():
    try:
        print("📌 Route hit")

        credentials = service_account.Credentials.from_service_account_file(
            KEY_PATH,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"]
        )

        client = BetaAnalyticsDataClient(credentials=credentials)

        request = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
            ],
            date_ranges=[
                DateRange(start_date="7daysAgo", end_date="today")
            ]
        )

        response = client.run_report(request)

        return {
            "sessions": response.rows[0].metric_values[0].value,
            "users": response.rows[0].metric_values[1].value
        }

    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print("❌ Full traceback:\n", traceback_str)

        # Return the full traceback in the API response
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "traceback": traceback_str}
        )