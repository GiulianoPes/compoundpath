export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  
  const { ticker, interval, period1, period2, range } = req.query;
  
  if (!ticker) {
    return res.status(400).json({ error: 'Missing ticker' });
  }

  try {
    let url;
    if (period1 && period2) {
      url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=${interval||'1mo'}&period1=${period1}&period2=${period2}`;
    } else {
      url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=${interval||'5m'}&range=${range||'1d'}`;
    }

    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
      }
    });

    if (!response.ok) {
      return res.status(response.status).json({ error: 'Yahoo Finance error' });
    }

    const data = await response.json();
    res.setHeader('Cache-Control', 's-maxage=300');
    return res.status(200).json(data);
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}
