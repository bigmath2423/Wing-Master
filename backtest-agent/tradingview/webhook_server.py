"""Récepteur de webhooks TradingView.

TradingView (compte payant) peut envoyer une alerte à une URL. Ce petit serveur
reçoit le JSON émis par strategy_template.pine et l'ajoute à un CSV que l'agent
sait analyser. Utile pour le suivi FORWARD (temps réel) en complément du backtest
historique exporté via le Strategy Tester.

Lancement :
    pip install flask
    python tradingview/webhook_server.py --out data/live_trades.csv --port 8080

Puis, dans l'alerte TradingView, mets l'URL publique (ngrok/serveur) + comme
message : {{strategy.order.alert_message}} ou le message de l'alerte Pine.
"""

from __future__ import annotations

import argparse
import csv
import json
import threading
from pathlib import Path

try:
    from flask import Flask, request, jsonify
except ImportError:  # message clair si Flask absent
    raise SystemExit("Flask requis : pip install flask")

app = Flask(__name__)
_lock = threading.Lock()
OUT_PATH = Path("data/live_trades.csv")

FIELDS = ["datetime", "symbol", "timeframe", "direction", "entry_price",
          "stop_loss", "take_profit", "confidence", "atr", "ob", "fvg",
          "sweep", "vwap_up", "structure_up", "raw"]


def _append_row(payload: dict) -> None:
    with _lock:
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        new_file = not OUT_PATH.exists()
        with OUT_PATH.open("a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
            if new_file:
                writer.writeheader()
            row = {k: payload.get(k) for k in FIELDS}
            row["raw"] = json.dumps(payload, ensure_ascii=False)
            writer.writerow(row)


@app.post("/tradingview")
def tradingview_hook():
    # TradingView envoie soit du JSON, soit du texte brut contenant du JSON.
    raw = request.get_data(as_text=True).strip()
    try:
        payload = request.get_json(force=True, silent=True) or json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return jsonify({"status": "error", "reason": "payload non-JSON", "raw": raw}), 400
    _append_row(payload)
    return jsonify({"status": "ok", "stored_in": str(OUT_PATH)}), 200


@app.get("/health")
def health():
    return jsonify({"status": "up", "out": str(OUT_PATH)})


def main() -> None:
    global OUT_PATH
    ap = argparse.ArgumentParser(description="Webhook receiver TradingView -> CSV")
    ap.add_argument("--out", default="data/live_trades.csv", help="CSV de sortie")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8080)
    args = ap.parse_args()
    OUT_PATH = Path(args.out)
    print(f"[webhook] écoute sur {args.host}:{args.port}, écrit dans {OUT_PATH}")
    app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
