export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');

  const { isin } = req.query;
  if (!isin) return res.status(400).json({ error: 'Missing ISIN' });

  try {
    // Try justETF search
    const url = `https://www.justetf.com/api/etfs?isin=${isin}&locale=en&valuation=EUR`;
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
      }
    });

    if (response.ok) {
      const data = await response.json();
      if (data.values && data.values.length > 0) {
        const etf = data.values[0];
        return res.status(200).json({
          isin: etf.isin,
          name: etf.name,
          ticker: etf.ticker || null,
          ter: etf.ter,
          currency: etf.currency,
          type: 'ETF',
          source: 'justETF'
        });
      }
    }

    // Fallback: try Yahoo Finance search
    const yhUrl = `https://query1.finance.yahoo.com/v1/finance/search?q=${isin}&quotesCount=5&newsCount=0`;
    const yhRes = await fetch(yhUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
      }
    });

    if (yhRes.ok) {
      const yhData = await yhRes.json();
      const quotes = yhData.quotes || [];
      if (quotes.length > 0) {
        const q = quotes[0];
        return res.status(200).json({
          isin,
          name: q.longname || q.shortname || q.symbol,
          ticker: q.symbol,
          type: q.quoteType || 'ETF',
          exchange: q.exchange,
          source: 'yahoo'
        });
      }
    }

    return res.status(404).json({ error: 'ISIN not found' });
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}