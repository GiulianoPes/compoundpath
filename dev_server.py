"""
Local development server.
Serves index.html as root and exposes the same /api/chart endpoint
that Vercel runs as a serverless function in production.

Usage:
    pip install flask yfinance
    python dev_server.py
Then open http://localhost:3000
"""
from flask import Flask, request, jsonify, send_from_directory
import yfinance as yf
import math
from datetime import datetime, timezone
import os

app = Flask(__name__, static_folder=os.path.dirname(__file__))


@app.route("/")
def index():
    return send_from_directory(os.path.dirname(__file__), "index.html")


@app.route("/api/chart")
def chart():
    ticker   = request.args.get("ticker",   "")
    interval = request.args.get("interval", "1mo")
    range_p  = request.args.get("range")
    period1  = request.args.get("period1")
    period2  = request.args.get("period2")

    if not ticker:
        return jsonify({"error": "ticker is required"}), 400

    try:
        t = yf.Ticker(ticker)

        if period1 and period2:
            start = datetime.fromtimestamp(int(period1), tz=timezone.utc)
            end   = datetime.fromtimestamp(int(period2),   tz=timezone.utc)
            hist  = t.history(start=start, end=end, interval=interval)
        else:
            hist = t.history(period=range_p or "1y", interval=interval)

        if hist.empty:
            return jsonify({"error": "no data found for " + ticker}), 404

        timestamps = [int(ts.timestamp()) for ts in hist.index]
        closes = [
            None if math.isnan(float(v)) else round(float(v), 4)
            for v in hist["Close"].tolist()
        ]

        resp = jsonify({"timestamps": timestamps, "closes": closes})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    print("CompoundPath dev server → http://localhost:3000")
    app.run(port=3000, debug=True)
