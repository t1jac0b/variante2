import os
from flask import Flask, jsonify, render_template, request, send_file

from chatbot.chatbot import Chatbot

PYTHONANYWHERE_USERNAME = "carvice"
PYTHONANYWHERE_WEBAPPNAME = "mysite"

app = Flask(__name__)

my_type_role = """
   Wenn ein Benutzer eine Frage zu einer Gedächtnislücke stellt, antworte direkt auf die gestellte Frage, indem du die Informationen, die der Benutzer bereits gegeben hat, berücksichtigst und in deine Antwort einbeziehst. Falls die Information, die der Benutzer zu erinnern versucht, nicht sofort klar ist, stelle geschlossene Fragen, um den Erinnerungsprozess zu unterstützen. Diese Fragen sollten darauf abzielen, den Benutzer durch Ja-oder-Nein-Antworten oder die Auswahl aus begrenzten Optionen zu leiten, um schnell spezifische Details zu identifizieren, die beim Erinnern helfen könnten.
Beispiele für solche Fragen könnten sein:
Handelt es sich bei dem, was Sie zu erinnern versuchen, um eine Person, einen Ort oder ein Ereignis?
Ist diese Information mit einem bestimmten Jahr oder einer bestimmten Zeitperiode verbunden?
Erinnern Sie sich, ob Sie diese Information im Rahmen Ihrer Arbeit oder in Ihrer Freizeit benötigt haben?
War diese Information mit einer bestimmten Emotion oder einem besonderen Ereignis verbunden?
Ziel dieser Methode ist es, durch gezielte, geschlossene Fragen den Benutzer effizient und methodisch dabei zu unterstützen, sich besser an die gesuchte Information zu erinnern
"""

my_instance_context = """
    
"""

my_instance_starter = """
Begrüsse freundliche den user und stell dich mit deinem Namen «ChatBob» vor und frage ihn zuerst nach seinem Namen und danach bei was er eine Gedankenstütze braucht.  
"""

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="chatbot2",
    user_id="chatbot2",
    type_name="Gedankensunterstützer",
    type_role=my_type_role,
    instance_context=my_instance_context,
    instance_starter=my_instance_starter
)

bot.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/mockups.pdf', methods=['GET'])
def get_first_pdf():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    files = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f))]
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    if pdf_files:
        # Get the path to the first PDF file
        pdf_path = os.path.join(script_directory, pdf_files[0])

        # Send the PDF file as a response
        return send_file(pdf_path, as_attachment=True)

    return "No PDF file found in the root folder."

@app.route("/<type_id>/<user_id>/chat")
def chatbot(type_id: str, user_id: str):
    return render_template("chat.html")


@app.route("/<type_id>/<user_id>/info")
def info_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: dict[str, str] = bot.info_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/conversation")
def conversation_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: list[dict[str, str]] = bot.conversation_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/response_for", methods=["POST"])
def response_for(type_id: str, user_id: str):
    user_says = None
    # content_type = request.headers.get('Content-Type')
    # if (content_type == 'application/json; charset=utf-8'):
    user_says = request.json
    # else:
    #    return jsonify('/response_for request must have content_type == application/json')

    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    assistant_says_list: list[str] = bot.respond(user_says)
    response: dict[str, str] = {
        "user_says": user_says,
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)


@app.route("/<type_id>/<user_id>/reset", methods=["DELETE"])
def reset(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    bot.reset()
    assistant_says_list: list[str] = bot.start()
    response: dict[str, str] = {
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)
