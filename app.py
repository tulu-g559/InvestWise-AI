from flask import Flask, render_template, request, jsonify
from yahooquery import Ticker
import pandas as pd
import requests, csv, datetime, logging

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

####### STOCK MARKET DATA (NIFTY 50, SENSEX, BANK NIFTY) ########
@app.route('/api/stocks', methods=['GET'])
def get_stock_data():
    stocks = ["^NSEI", "^BSESN", "^NSEBANK"]  # NIFTY 50, SENSEX, BANK NIFTY
    tickers = Ticker(stocks)
    data = tickers.price

    stock_data = []
    for stock in stocks:
        stock_info = data.get(stock, {})  # Safely fetch data
        stock_data.append({
            "name": stock_info.get("shortName", stock),
            "price": stock_info.get("regularMarketPrice", "N/A"),
            "change": stock_info.get("regularMarketChange", "N/A"),
            "percent_change": stock_info.get("regularMarketChangePercent", "N/A")
        })

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(stock_data)  # Return JSON for AJAX

    return render_template("stocks.html", stocks=stock_data)  # Render HTML for direct access

###### INVESTMENT RECOMMENDATIONS ######
file_path = "C:/Users/Arnab/OneDrive/Desktop/cleaned_dataset.csv"  # Relative path to ensure portability
df = pd.read_csv(file_path)

# Map risk levels
risk_mapping = {1: "low", 2: "medium", 3: "high", 4: "high", 5: "high", 6: "high", 7: "high"}
df["risk_level"] = df["risk_level"].map(risk_mapping)

# Convert return_rate to float
df["return_rate"] = df["return_rate"].astype(str).str.replace("%", "", regex=False)
df["return_rate"] = pd.to_numeric(df["return_rate"], errors="coerce")

# Convert min_investment to numeric
df["min_investment"] = pd.to_numeric(df["min_investment"], errors="coerce")

def recommend_stocks(min_investment, risk_level, top_n=5):
    filtered_df = df.query("min_investment <= @min_investment and risk_level == @risk_level")
    recommended = filtered_df.nlargest(top_n, "return_rate")
    return recommended[["Names", "Category", "risk_level", "min_investment", "return_rate"]].to_dict(orient="records")

@app.route("/reco", methods=["GET", "POST"])
def investment_recommendations():
    recommendations, error = [], None
    if request.method == "POST":
        try:
            min_investment = int(request.form.get("min_investment", 0))
            risk_level = request.form.get("risk_level", "").lower()

            if risk_level not in ["low", "medium", "high"]:
                error = "Invalid risk level. Choose from 'low', 'medium', or 'high'."
            else:
                recommendations = recommend_stocks(min_investment, risk_level)
        except Exception as e:
            error = str(e)
    
    return render_template("invest_reco.html", recommendations=recommendations, error=error)

###### CHATBOT ######
@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

###### INVESTMENTS PAGE ######
@app.route("/investments")
def investments():
    return render_template("investments.html")

###### MARKET DATA ######
GOOGLE_SHEETS_BASE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRWAl7HcCZ49EJRSKLVCTkaTApQwYuVn1DaWTgBvVWBInWtPoUGhHpgN2he-lhxpHHnww_d7eM1fV6a/pub?output=csv&gid="

# Mapping sheet names to their respective 'gid' values
SHEET_MAPPING = {
    "NIFTY Bank": "0",
    "Sensex": "1425646191",
    "FINNIFTY": "1706389967",
    "NIFTY 100": "1539449181",
    "NIFTY Midcap Select": "2059264003"
}

def fetch_google_sheets_data(sheet_name):
    try:
        gid = SHEET_MAPPING.get(sheet_name)
        if not gid:
            return {"error": f"Sheet '{sheet_name}' not found."}

        sheet_url = f"{GOOGLE_SHEETS_BASE_URL}{gid}"
        response = requests.get(sheet_url, timeout=5)
        response.raise_for_status()

        data = response.text.splitlines()
        reader = csv.reader(data)

        headers = next(reader, None)
        if not headers:
            return {"error": "Invalid CSV format."}

        rows = [row for row in reader]

        return {"headers": headers, "data": rows}

    except requests.RequestException as e:
        logging.error(f"Error fetching Google Sheets data: {e}")
        return {"error": str(e)}

@app.route("/market_data")
def market_data():
    default_sheet = "Nifty Bank"  # Default sheet
    stocks = fetch_google_sheets_data(default_sheet)
    
    stock_data = {
        'dates': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'prices': [150, 155, 160],
    }
    return render_template("market_data.html", sheets=SHEET_MAPPING.keys(), stocks=stocks, stock_data=stock_data)

@app.route('/get_data')
def get_data():
    sheet_name = request.args.get('sheet_name')
    if not sheet_name or sheet_name not in SHEET_MAPPING:
        return jsonify({"error": "Invalid or missing sheet name"}), 400

    data = fetch_google_sheets_data(sheet_name)
    return jsonify(data)

###### PROFILE ######
@app.route("/profile")
def profile():
    user = {
        "name": "Arnab Ghosh",
        "email": "garnab559@gmail.com",
        "join_date": "2024-01-15"
    }
    return render_template("profile.html", user=user)

@app.route("/edit_profile")
def edit_profile():
    return "<h1>Kal k krbe</h1>"

###### ANALYTICS ######
@app.route("/analytics")
def analytics():
    return render_template("analytics.html")

###### RUN FLASK APP ######
if __name__ == "__main__":
    app.run(debug=True)
