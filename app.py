import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO
import yaml
from flask import Flask, render_template, request, jsonify
from aio_handler import AIOHandler, read_seat_data
import numpy as np
import socket
import threading
import time
import os
import csv
import pandas as pd  # Ajout de l'import pandas

class TCPClient:
    def __init__(self, host, port, callback):
        self.host = host
        self.port = port
        self.callback = callback

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print(f"Connexion TCP vers {self.host}:{self.port}")
                sock.connect((self.host, self.port))
                print("TCP connecté")
                buffer = ""
                while True:
                    data = sock.recv(4096)
                    if not data:
                        print("TCP: connexion fermée par le pair, tentative de reconnexion...")
                        break
                    buffer += data.decode()
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            try:
                                self.callback(line)
                            except Exception as cb_e:
                                print(f"Erreur dans le callback lors du traitement d'une ligne : {cb_e}")
            except Exception as e:
                print(f"Erreur de connexion TCP: {e}. Reconnexion dans 1s...")
            time.sleep(1)

# Flask
app = Flask(__name__)
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    serve_client=True,
)

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
    try:
        body = None
        try:
            body = request.get_json(force=False)
        except Exception:
            body = None

        if 'handler' not in globals() or handler is None:
            return jsonify({"ocs_class": "Unknown", "error": "handler not ready"}), 500

        clf = getattr(handler, 'classifier', None)
        if clf is None:
            return jsonify({"ocs_class": "Unknown", "error": "no classifier configured"}), 200

        raw = None
        if body and isinstance(body, dict):
            if 'frame' in body and isinstance(body['frame'], list) and len(body['frame']) >= 10:
                raw = np.array([body['frame'][:10]], dtype=float)
            elif 'offset' in body and isinstance(body['offset'], list) and len(body['offset']) >= 10:
                raw = np.array([body['offset'][:10]], dtype=float)

        if raw is None:
            aio = getattr(handler, 'aio_data', None)
            if not aio:
                return jsonify({"ocs_class": "Unknown", "error": "no frame available"}), 400
            raw = read_seat_data(aio)

        Xc = preprocess_ocs(raw)

        if hasattr(clf, 'predict_proba'):
            probs = clf.predict_proba(Xc)
            cls = int(clf.predict(Xc)[0])
            prob = float(np.max(probs[0]))
        else:
            cls = int(clf.predict(Xc)[0])
            prob = None

        return jsonify({"ocs_class": int(cls), "prob": prob}), 200

    except Exception as e:
        print('Error in /api/predict_ocs:', e)
        return jsonify({"ocs_class": "Error", "error": str(e)}), 500

@app.route('/api/dataset_zone_mean', methods=['GET'])
def dataset_zone_mean():
    try:
        w = float(request.args.get('weight', None))
    except Exception:
        return jsonify({"error": "invalid weight"}), 400

    try:
        margin = float(request.args.get('margin', 5))
    except Exception:
        margin = 5.0

    person = request.args.get('person', None)
    csv_name = request.args.get('csv', None)

    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    sensor_cols = ['C1','C2','C3','C4','C5','C6','C7','C8','C9','C10']
    sums = [0.0] * 10
    count = 0
    found_weights = []   # ← AJOUT

    low = w - margin
    high = w + margin

    if not os.path.isdir(data_dir):
        return jsonify({"error": "data directory not found"}), 500

    files_to_scan = []
    if csv_name:
        safe_name = os.path.basename(csv_name)
        path = os.path.join(data_dir, safe_name)
        if os.path.exists(path):
            files_to_scan = [path]
        else:
            return jsonify({"error": f"csv '{safe_name}' not found in data directory"}), 400
    else:
        default_csv = '04_df_feature.csv'
        default_path = os.path.join(data_dir, default_csv)
        if os.path.exists(default_path):
            files_to_scan = [default_path]
        else:
            return jsonify({"error": f"default csv '{default_csv}' not found in data directory"}), 400

    for path in files_to_scan:
        fname = os.path.basename(path)
        try:
            with open(path, 'r') as fh:
                reader = csv.DictReader(fh)
                fn = reader.fieldnames or []
                offset_cols = [f'C{i}_offset' for i in range(1, 11)]
                simple_cols = ['C1','C2','C3','C4','C5','C6','C7','C8','C9','C10']
                if all(c in fn for c in offset_cols):
                    sensor_cols_file = offset_cols
                elif all(c in fn for c in simple_cols):
                    sensor_cols_file = simple_cols
                else:
                    sensor_cols_file = [c for c in offset_cols if c in fn]
                    if len(sensor_cols_file) != 10:
                        sensor_cols_file = [c for c in simple_cols if c in fn]

                for row in reader:
                    try:
                        wt = float(row.get('Weight') or row.get('Weight') or 0)
                    except Exception:
                        continue
                    if wt < low or wt > high:
                        continue

                    if person:
                        person_cols = ['ID', 'person', 'name', 'person_name']
                        row_person = None
                        for pc in person_cols:
                            v = row.get(pc)
                            if v:
                                row_person = str(v).strip()
                                break
                        if row_person is None:
                            if person.lower() in fname.lower():
                                row_person = person
                        if row_person is None or row_person.lower() != person.strip().lower():
                            continue

                    ok = True
                    vals = []
                    cols_to_use = sensor_cols_file if sensor_cols_file and len(sensor_cols_file) == 10 else sensor_cols
                    for i, col in enumerate(cols_to_use):
                        try:
                            v = float(row.get(col, 0))
                        except Exception:
                            ok = False
                            break
                        vals.append(v)
                    if not ok:
                        continue
                    for i, v in enumerate(vals):
                        sums[i] += v
                    count += 1
                    found_weights.append(wt)   # ← AJOUT
        except Exception as e:
            print(f"Error reading {path}: {e}")

    if count == 0:
        return jsonify({"mean": None, "n": 0, "weights": []})

    means = [s / count for s in sums]
    means_scaled = [m / 1000.0 for m in means]
    return jsonify({"mean": means_scaled, "n": count, "weights": found_weights})   # ← AJOUT weights
if __name__ == "__main__":
    # Charger config TCP
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    MODEL_PATHS = {
        "SVR_lt120": "exported_models/SVR_final_lt120.pkl",
       "weight_SVR": "exported_models/weight_pred_SVR.pkl",
        "weight_pred": "exported_models/weight_pred.pkl",
        "fav": "exported_models/fav.pkl"
    }
    
    print("A")
    handler = AIOHandler(
        config=config,
        model_paths=MODEL_PATHS,
        socketio=socketio
    )
    tcp_client = TCPClient(
        host="127.0.0.1",
        port=5001,
        callback=handler.on_aio_receive
    )

    tcp_client.start()
    
    @socketio.on('start_prediction')
    def handle_start_prediction(data=None):
        try:
            name = None
            if isinstance(data, dict):
                name = data.get('person_name')
            handler.start_prediction(name)
        except Exception as e:
            print('Error handling start_prediction event:', e)
    
    print("B")
    print("C")
    print("Frontend disponible sur http://localhost:5000")

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False,
    )