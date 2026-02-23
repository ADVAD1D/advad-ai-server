from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

#advad server for api llm in the game
#note: If the server experiences increased traffic in the future, will need to migrate to FastAPI.
#Init flask app
app = Flask(__name__)

def get_real_ip():
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    else:
        return request.remote_addr

#Rate limiter
limiter = Limiter(app=app, key_func=get_real_ip, storage_uri="memory://")
#the memory storage is for save the rate limit data

app.url_map.strict_slashes = False

#logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#env config
load_dotenv()
CORS(app)

API_KEY = os.getenv("GEMINI_API_KEY")
APP_TOKEN = os.getenv("APP_TOKEN")

if not API_KEY:
    # Esto es mejor imprimirlo en consola que lanzar raise error para que Render no crashee en el build
    print("GEMINI_API_KEY environment variable not set")

else:
    genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""
    CRITICAL RULE / REGLA CRÍTICA: You MUST always respond in the exact same language the user uses to speak to you. If the user writes in English, reply in English. Si el usuario escribe en español, responde en español.

    Eres una inteligencia artificial de entrenamiento para soldados espaciales de "La Organización". Tu tono debe ser exigente, motivador y militar.

    Información de apoyo (debes traducirla al idioma del jugador al responder):
    - Movimiento: Te mueves con WASD o con las flechas.
    - Acciones: Disparas con la barra espaciadora, haces dash con la tecla E.
    
    Códigos especiales:
    - Si el jugador escribe exactamente "CYB3R4R3N4": Significa que ha superado la primera arena. Felicítalo y dile que una próxima arena se aproxima.
    """
)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Rate limit exceeded",
        "message": "Has enviado muchos mensajes, espera un momento soldado."
    }), 429

@app.route("/", methods=["GET"])
def home():
    logger.info("Home endpoint accessed")
    return "Advad AI Server is running!", 200 #OK

@app.route("/askai", methods=["POST"])
@limiter.limit("10 per minute")
def ask_ai():
    auth_header = request.headers.get("X-App-Token")
    if auth_header != APP_TOKEN:
        return jsonify({
            "error": "Access denied"
        }), 403 #Forbidden
    
    if not API_KEY:
        return jsonify({"error": "GEMINI_API_KEY environment variable not set"}), 500
    
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400 #Bad Request
        
        response = model.generate_content(prompt)

        return jsonify({"response": response.text}), 200 #OK
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500 #Internal Server Error

    #prueba local
    #Invoke-RestMethod -Uri "http://localhost:10000/askai" -Method Post -ContentType "application/json; charset=utf-8" -Body '{"prompt": "Señor, reporte de situación."}'
    #curl -X POST http://localhost:10000/askai \-H "Content-Type: application/json" \-d '{"prompt": "Señor, solicito instrucciones."}'


#configuration for render    
if __name__ == "__main__":
    #render uses gunicorn, recomended in port 10000
    app.run(host="0.0.0.0", port=10000)
