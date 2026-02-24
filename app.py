from flask import Flask, request, jsonify
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
    return "카페24 콜백 서버 정상 작동 중"

@app.route("/callback")
def callback():
    code = request.args.get("code", "")
    state = request.args.get("state", "")
    error = request.args.get("error", "")

    if error or not code:
        return "<h2>인증 실패: " + (error or "코드 없음") + "</h2>"

    try:
        hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "localhost")
        res = requests.post(
            "https://" + CAFE24_MALL_ID + ".cafe24api.com/api/v2/oauth/token",
            auth=(CAFE24_CLIENT_ID, CAFE24_CLIENT_SECRET),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": "https://" + hostname + "/callback"
            }
        )
        data = res.json()
        token = data.get("access_token", "")

        if not token:
            return "<h2>토큰 발급 실패</h2><p>" + str(data) + "</p>"

        token_store["latest"] = {
            "access_token": token,
            "refresh_token": data.get("refresh_token", "")
        }

        return """<!DOCTYPE html>
<html>
<body style="font-family:sans-serif;text-align:center;padding:60px;background:#0f0f0f;color:#f5f5f7;">
<h2 style="color:#c9a84c;">카페24 인증 완료!</h2>
<p style="color:#86868b;margin-bottom:30px;">아래 버튼을 클릭해서 앱으로 돌아가세요.</p>
<p style="color:#c9a84c;font-size:1.1rem;">이제 쇼핑몰 매니저 탭으로 돌아가서<br>"✅ 인증 완료 확인" 버튼을 클릭하세요!</p> style="background:#c9a84c;color:#000;font-weight:700;
padding:14px 28px;border-radius:10px;text-decoration:none;font-size:1rem;">
쇼핑몰 매니저로 돌아가기
</a>
</body>
</html>"""

    except Exception as e:
        return "<h2>오류: " + str(e) + "</h2>"

@app.route("/token")
def get_token():
    if "latest" in token_store:
        token_data = token_store.pop("latest")
        return jsonify(token_data)
    return jsonify({"error": "token_not_found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
