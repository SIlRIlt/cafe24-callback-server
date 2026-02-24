from flask import Flask, request, redirect, jsonify
import requests
import os

app = Flask(__name__)

CAFE24_MALL_ID = os.environ.get("CAFE24_MALL_ID", "")
CAFE24_CLIENT_ID = os.environ.get("CAFE24_CLIENT_ID", "")
CAFE24_CLIENT_SECRET = os.environ.get("CAFE24_CLIENT_SECRET", "")
STREAMLIT_URL = os.environ.get("STREAMLIT_URL", "https://siritt.streamlit.app")

token_store = {}

@app.route("/")
def index():
    return "카페24 콜백 서버 정상 작동 중 ✅"

@app.route("/callback")
def callback():
    code = request.args.get("code", "")
    state = request.args.get("state", "")
    error = request.args.get("error", "")
    if error:
        return redirect(f"{STREAMLIT_URL}?cafe24_error={error}")
    if not code:
        return redirect(f"{STREAMLIT_URL}?cafe24_error=no_code")
    try:
        hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "localhost")
        res = requests.post(
            f"https://{CAFE24_MALL_ID}.cafe24api.com/api/v2/oauth/token",
            auth=(CAFE24_CLIENT_ID, CAFE24_CLIENT_SECRET),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": f"https://{hostname}/callback"
            }
        )
        data = res.json()
        token = data.get("access_token", "")
        refresh_token = data.get("refresh_token", "")
        if not token:
            return redirect(f"{STREAMLIT_URL}?cafe24_error=token_failed")
        token_store[state] = {"access_token": token, "refresh_token": refresh_token}
        return redirect(f"{STREAMLIT_URL}?cafe24_state={state}")
    except Exception as e:
        return redirect(f"{STREAMLIT_URL}?cafe24_error={str(e)}")

@app.route("/token")
def get_token():
    state = request.args.get("state", "")
    if state in token_store:
        token_data = token_store.pop(state)
        return jsonify(token_data)
    return jsonify({"error": "token_not_found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
