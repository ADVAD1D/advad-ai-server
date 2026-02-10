from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

#Init flask app
app = Flask(__name__)

def get_real_ip():
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    else:
        return request.remote_addr

#Rate limiter
limiter = Limiter(app=app, key_func=get_real_ip, storage_uri="memory://")

#logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#env config
load_dotenv()
CORS(app)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    # Esto es mejor imprimirlo en consola que lanzar raise error para que Render no crashee en el build
    print("GEMINI_API_KEY environment variable not set")

else:
    genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash",
                              system_instruction="Eres una inteligencia artificial de entrenamiento para soldados espaciales"
                              "responde a los soldados de la organización y exígeles lo mejor de ellos mismos.")

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
    #render uses unicorn, recomended in port 10000
    app.run(host="0.0.0.0", port=10000)
