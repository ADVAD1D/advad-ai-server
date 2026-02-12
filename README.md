# 🪐 Advad‑AI‑Server

A tiny Flask‑based API that proxies requests to Google’s Gemini LLM.  
Designed to be embedded in a Godot game so your project can **consume a language‑model API securely and with rate‑limiting**.

> ⚠️ **Security note**  
> The server expects requests to carry an `X‑App‑Token` header; keep this token secret in your game build.  
> The real LLM API key is read from an environment variable on the host machine.

---

## 📁 Repository structure

```
.
├── app.py            # main Flask application
├── requirements.txt  # Python dependencies
└── README.md         # this documentation
```

---

## 🧰 Features

- Single endpoint (`/askai`) to send prompts and receive generated text.
- Built‑in rate limiting (10 requests/minute per client IP).
- CORS enabled for cross‑origin calls from your Godot project.
- Simple token‑based authentication to prevent unauthorized use.
- Logging of endpoint hits and errors.
- Configurable model and system instruction for the Gemini API.

---

## 🚀 Setup

1. **Clone the repo**:

   ```bash
   git clone https://github.com/<your‑username>/advad-ai-server.git
   cd advad-ai-server
   ```

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   .\venv\Scripts\activate      # Windows
   # or
   source venv/bin/activate     # macOS / Linux
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:

   Create a `.env` file in the project root or set the variables in your deployment environment.

   ```ini
   GEMINI_API_KEY=your_real_gemini_key
   APP_TOKEN=some_secret_token_for_game
   ```

   - `GEMINI_API_KEY`: API key for Google Generative AI.
   - `APP_TOKEN`: Shared secret that your game will include in requests.

5. **Run locally**

   ```bash
   python app.py
   ```

   The server listens on `0.0.0.0:10000` by default (Render.com uses this port).

---

## 📡 API Endpoints

### `GET /`

Returns a simple health check.

**Response:**

```json
"Advad AI Server is running!"
```

### `POST /askai`

Send a prompt to the LLM.

- **Headers**
  - `Content-Type: application/json`
  - `X-App-Token: <APP_TOKEN>`
- **Body**

  ```json
  {
    "prompt": "Escribe una frase de ánimo para un soldado espacial."
  }
  ```

- **Responses**
  - `200` → `{ "response": "<text from model>" }`
  - `400` → missing prompt
  - `403` → invalid or missing app token
  - `429` → rate limit exceeded
  - `500` → internal error (e.g. missing API key)

> Rate limit: 10 requests per minute per client IP.  
> When exceeded, you receive:

```json
{
  "error": "Rate limit exceeded",
  "message": "Has enviado muchos mensajes, espera un momento soldado."
}
```

---

## 🕹️ Example: Godot Integration

Here’s a minimal GDScript snippet that talks to the server:

```gdscript
var SERVER_URL = "http://localhost:10000/askai"
var APP_TOKEN   = "some_secret_token_for_game"

func ask_ai(prompt: String) -> void:
    var http := HTTPRequest.new()
    add_child(http)
    http.connect("request_completed", self, "_on_response")
    var headers = ["Content-Type: application/json",
                   "X-App-Token: %s" % APP_TOKEN]
    var body = to_json({"prompt": prompt})
    http.request(SERVER_URL, headers, true, HTTPClient.METHOD_POST, body)

func _on_response(result, response_code, headers, body):
    if response_code == 200:
        var data = parse_json(body.get_string_from_utf8())
        print("AI says: ", data["response"])
    else:
        print("Error from server: ", response_code, body.get_string_from_utf8())
```

> ⚠️ **Remember**: keep `APP_TOKEN` private. For a release build, obfuscate or fetch it securely.

---

## 🛠 Deployment

The code is compatible with many PaaS providers (Render.com, Heroku, etc.).  
They usually set environment variables via a dashboard and run `python app.py` or use Gunicorn:

```bash
gunicorn app:app -b 0.0.0.0:10000
```

---

## 📦 `requirements.txt`

```txt
Flask
flask-cors
flask-limiter
python-dotenv
google-generativeai
```

---

## 📝 Customization

- **Change model or instruction**  
  Edit the `model = genai.GenerativeModel(...)` block in `app.py`.

- **Adjust rate limiting**  
  Modify `@limiter.limit("10 per minute")`.

- **Logging level**  
  Change `logging.basicConfig(level=logging.INFO)` to `DEBUG` for more verbosity.

---

## 🧾 License & Contribution

Feel free to fork, modify, or integrate this microserver into your own projects.  
Contributions and issues are welcome.

---

> ✅ Ready for use with your Godot game.  
> 💡 Bonus: you can expand this server with new endpoints—dialogue history, user IDs, etc., as your AI-driven gameplay grows.