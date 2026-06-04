from http.server import BaseHTTPRequestHandler
import yfinance as yf
import json
import math
from urllib.parse import parse_qs, urlparse
from datetime import datetime, timezone


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        try:
            params = parse_qs(urlparse(self.path).query)
            ticker   = params.get("ticker",   [""])[0]
            interval = params.get("interval", ["1mo"])[0]
            range_p  = params.get("range",    [None])[0]
            period1  = params.get("period1",  [None])[0]
            period2  = params.get("period2",  [None])[0]

            if not ticker:
                return self._respond(400, {"error": "ticker is required"})

            t = yf.Ticker(ticker)

            if period1 and period2:
                start = datetime.fromtimestamp(int(period1), tz=timezone.utc)
                end   = datetime.fromtimestamp(int(period2),   tz=timezone.utc)
                hist  = t.history(start=start, end=end, interval=interval)
            else:
                hist = t.history(period=range_p or "1y", interval=interval)

            if hist.empty:
                return self._respond(404, {"error": "no data found for " + ticker})

            timestamps = [int(ts.timestamp()) for ts in hist.index]
            closes = [
                None if math.isnan(float(v)) else round(float(v), 4)
                for v in hist["Close"].tolist()
            ]

            self._respond(200, {"timestamps": timestamps, "closes": closes})

        except Exception as exc:
            self._respond(500, {"error": str(exc)})

    # ── helpers ──────────────────────────────────────────────────────────────

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _respond(self, status: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass  # silence default HTTP logs
