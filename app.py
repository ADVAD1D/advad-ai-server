from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
from dotenv import load_dotenv

app = Flask(__name__)

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

@app.route("/", methods=["GET"])

def home():
    return "Advad AI Server is running!", 200 #OK

@app.route("/askai", methods=["POST"])

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
