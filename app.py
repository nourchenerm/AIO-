from flask import Flask, render_template
from flask_socketio import SocketIO
import yaml
from flask import Flask, render_template, request, jsonify
from aio_handler import AIOHandler
import socket
import threading

class TCPClient:

    def __init__(self, host, port, callback):
        self.host = host
        self.port = port
        self.callback = callback

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(f"Connexion TCP vers {self.host}:{self.port}")
        sock.connect((self.host, self.port))

        print("TCP connecté")

        buffer = ""

        while True:

            data = sock.recv(4096)

            if not data:
                break

            buffer += data.decode()

            while '\n' in buffer:

                line, buffer = buffer.split('\n', 1)

                if line.strip():
                    self.callback(line)
# Flask
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Route principale
@app.route("/")
def index():
    return render_template("index.html")
@app.route('/api/predict_weight', methods=['POST'])
def predict_weight():

    data = request.get_json()
    real_weight = data.get("real_weight", 0)

    return jsonify({
        "results": [
            {
                "model": "LightGBM",
                "predicted": 72.5
            }
        ]
    })
@app.route('/api/predict_ocs', methods=['POST'])
def predict_ocs():

    return jsonify({
        "ocs_class": "Adult"
    })
if __name__ == "__main__":

    # Charger config TCP
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    MODEL_PATHS = {
        "LightGBM": "exported_models/lightgbm_final.pkl",
        "SVR": "exported_models/svr_final.pkl",
        "RandomForest_lt100": "exported_models/randomforest_final_lt100.pkl",
        "LightGBM_lt100": "exported_models/lightgbm_final_lt100.pkl",
        "SVR_lt100": "exported_models/svr_final_lt100.pkl",
    }
    
    print("A")
    handler = AIOHandler(
        config=config,
        model_paths=MODEL_PATHS,
        socketio=socketio
    )
    tcp_client = TCPClient(
        host="0.0.0.0",
        port=5001,
        callback=handler.on_aio_receive
    )

    tcp_client.start()
    @socketio.on('start_prediction')
    def handle_start_prediction():
        handler.start_prediction()
    print("B")

    #handler.aio_protocol.on_receive = handler.on_aio_receive
    print("C")

    print("Frontend disponible sur http://localhost:5000")

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True
    )