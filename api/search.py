from http.server import BaseHTTPRequestHandler
import urllib.request
import json
from urllib.parse import parse_qs, urlparse


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)
        q = params.get("q", [""])[0].strip()

        if not q or len(q) < 2:
            return self._respond(400, {"error": "query too short"})

        try:
            url = (
                "https://query1.finance.yahoo.com/v1/finance/search"
                f"?q={urllib.parse.quote(q)}&quotesCount=10&newsCount=0"
                "&enableFuzzyQuery=false&enableCb=false"
            )
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read())

            quotes = data.get("quotes", [])
            results = []
            for item in quotes:
                symbol = item.get("symbol", "")
                name   = item.get("longname") or item.get("shortname") or symbol
                qtype  = item.get("quoteType", "")
                # map Yahoo quoteType to our type labels
                type_map = {
                    "ETF":          "ETF",
                    "EQUITY":       "Stock",
                    "CRYPTOCURRENCY": "Crypto",
                    "INDEX":        "Index",
                    "MUTUALFUND":   "Fund",
                }
                label = type_map.get(qtype, qtype)
                results.append({
                    "ticker": symbol,
                    "name":   name,
                    "type":   label,
                    "isin":   item.get("isin", "—"),
                    "exchange": item.get("exchDisp", ""),
                })

            self._respond(200, {"results": results})

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
        pass
