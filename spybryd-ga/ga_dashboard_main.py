from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension
from google.oauth2 import service_account
import json

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

KEY_PATH = "spybryd-3ef808c31aa4.json"
PROPERTY_ID = "376255082"

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <h2>Analytics Overview</h2>
            <label>Start Date: <input type="date" id="start_date" value="2024-01-01"></label>
            <label>End Date: <input type="date" id="end_date" value="2024-01-31"></label>
            <button onclick="fetchData()">Update</button>
            <canvas id="gaChart" width="600" height="400"></canvas>
            <script>
                async function fetchData() {
                    const start = document.getElementById("start_date").value;
                    const end = document.getElementById("end_date").value;
                    const response = await fetch(`/ga/overview?start_date=${start}&end_date=${end}`);
                    const data = await response.json();

                    const ctx = document.getElementById('gaChart').getContext('2d');
                    new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: ['Sessions', 'Users', 'Pageviews', 'Country Count'],
                            datasets: [{
                                label: 'GA Metrics',
                                data: [data.sessions, data.users, data.pageviews, data.countries],
                                backgroundColor: ["#3498db", "#2ecc71", "#f1c40f", "#e74c3c"]
                            }]
                        },
                        options: {
                            scales: { y: { beginAtZero: true } }
                        }
                    });
                }
                fetchData();
            </script>
        </body>
    </html>
    """

@app.get("/ga/overview")
async def get_analytics_overview(start_date: str, end_date: str):
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
            Metric(name="screenPageViews")
        ],
        dimensions=[
            Dimension(name="country")
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)]
    )

    response = client.run_report(request=request)

    sessions = int(response.rows[0].metric_values[0].value)
    users = int(response.rows[0].metric_values[1].value)
    pageviews = int(response.rows[0].metric_values[2].value)
    countries = len(response.rows)

    return {
        "sessions": sessions,
        "users": users,
        "pageviews": pageviews,
        "countries": countries
    }