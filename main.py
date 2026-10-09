import asyncio
import json
import os
import ssl
import certifi
import requests
import websockets
from dotenv import load_dotenv

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
load_dotenv()

# Configuration
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
if not DISCORD_WEBHOOK_URL:
    raise RuntimeError("DISCORD_WEBHOOK_URL is not set. Add it to your .env file.")

PRICE_ALERT_THRESHOLD = 2

# Track starting baseline price
baseline_price = None

async def send_alert(ticker, current_price, pct_change):
    direction = "🚀 INCREASE" if pct_change > 0 else "🔻 DROP"
    payload = {
        "embeds": [{
            "title": f"{direction}: {ticker}",
            "color": 65280 if pct_change > 0 else 16711680,
            "fields": [
                {"name": "Price", "value": f"${current_price:,.2f}", "inline": True},
                {"name": "Change", "value": f"{pct_change:+.2f}%", "inline": True}
            ]
        }]
    }
    try:
        await asyncio.to_thread(
            requests.post, DISCORD_WEBHOOK_URL, json=payload, timeout=10
        )
        print(f"[SENT ALERT] {ticker} {pct_change:+.2f}%")
    except Exception as e:
        print(f"[ERROR] Failed to send webhook: {e}")

async def stream_prices():
    global baseline_price
    url = "wss://stream.binance.com:9443/ws/btcusdt@trade"
    
    print("Connecting to Binance WebSocket...")
    async with websockets.connect(url, ssl=SSL_CONTEXT) as ws:
        print("Connected!...Listening for price changes...\n")
        
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            current_price = float(data['p'])
            
            if baseline_price is None:
                baseline_price = current_price
                print(f"Initial baseline price set to: ${baseline_price:,.2f}")
                continue
            
            # Calculate percentage change from baseline
            pct_change = ((current_price - baseline_price) / baseline_price) * 100
            
            print(f"Live Price: ${current_price:,.2f} | Change: {pct_change:+.3f}%", end="\r")
            
            # Check threshold trigger
            if abs(pct_change) >= PRICE_ALERT_THRESHOLD:
                await send_alert("BTC/USDT", current_price, pct_change)
                baseline_price = current_price  # Reset baseline after alert

if __name__ == "__main__":
    asyncio.run(stream_prices())