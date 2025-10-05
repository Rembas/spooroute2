import os
from flask import Flask, render_template, request
import requests

SUBMISSIONS = []  # in-memory, demo only
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY","dev")

    @app.route("/")
    def index():
        status = {"lines":[]}; bulletins = {"bulletins":[]}
        try: status = requests.get(f"{API_BASE}/api/v1/status", timeout=2).json()
        except: pass
        try: bulletins = requests.get(f"{API_BASE}/api/v1/bulletins", timeout=2).json()
        except: pass
        return render_template("index.html", status=status, bulletins=bulletins)

    @app.route("/alternatives")
    def alternatives():
        from_stop = request.args.get("from_stop","STOP_A")
        try:
            r = requests.get(f"{API_BASE}/api/v1/alternatives", params={"from_stop":from_stop}, timeout=2)
            data = r.json()
        except Exception:
            data = {"from_stop":from_stop, "alternatives":[]}
        return render_template("alternatives.html", data=data)
    
    @app.route("/report", methods=["GET", "POST"])
    def report():
        if request.method == "POST":
            data = {
                "line": request.form.get("line","").strip(),
                "stop_id": request.form.get("stop_id","").strip(),
                "type": request.form.get("type","other").strip(),
                "text": request.form.get("text","").strip(),
            }
            if not data["text"]:
                # Mostra il form con errore
                return render_template("report.html", error="Please add a short description."), 400
            SUBMISSIONS.append(data)  # solo demo
            return render_template("report_thanks.html", data=data)
        return render_template("report.html")

    @app.route("/admin")
    def admin():
        return render_template("admin/dashboard.html")

    @app.route("/admin/alerts")
    def admin_alerts():
        alerts = {}
        try:
            r = requests.get(f"{API_BASE}/api/v1/alerts", timeout=2)
            alerts = r.json()
        except Exception:
            alerts = {"alerts":[]}
        return render_template("admin/alerts.html", alerts=alerts)

    @app.route("/admin/feedback")
    def admin_feedback():
        return render_template("admin/feedback.html", feedback=SUBMISSIONS)

    @app.route("/_demo/crowd_count")
    def demo_crowd_count():
        from collections import Counter
        c = Counter([ (r.get("stop_id") or "unknown") for r in SUBMISSIONS ])
        return {"counts": c}
    
    @app.route("/admin/feeds")
    def admin_feeds():
        feeds = [
            {"name": "Kraków ZTP GTFS-RT", "status": "ok"},
            {"name": "GTFS static (demo)", "status": "pending"}
        ]
        return render_template("admin/feeds.html", feeds=feeds)

    @app.route("/plan")
    def plan_view():
        from_stop = request.args.get("from_stop","STOP_A")
        to_stop = request.args.get("to_stop","STOP_B")
        depart_at = int(request.args.get("depart_at","32400"))
        try:
            r = requests.get(f"{API_BASE}/api/v1/plan", params={
                "from_stop": from_stop,
                "to_stop": to_stop,
                "depart_at": depart_at
            }, timeout=3)
            data = r.json()
        except Exception:
            data = {"itineraries": []}
        return render_template("plan.html", data=data, qs={"from":from_stop, "to":to_stop})



    return app

if __name__ == "__main__":
    app = create_app()
    host = os.getenv("WEB_HOST", "0.0.0.0")
    port = int(os.getenv("WEB_PORT", "5000"))
    app.run(host=host, port=port, debug=True)