from flask import Blueprint, request, jsonify, current_app
from services.chat_service import chat

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json()

    messages = data.get("messages", [])

    data_dir = current_app.config["DATA_DIR"]

    reply = chat(messages, data_dir)

    return jsonify({"reply": reply})