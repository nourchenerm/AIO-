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
    """
    Retourne la moyenne des capteurs pour les données dont le poids est dans [weight - margin, weight + margin].
    Utilisé par le frontend pour afficher la comparaison "Real weight vs Dataset mean".
    """
    try:
        w = float(request.args.get('weight', None))
        if w is None:
            return jsonify({"error": "weight parameter is required"}), 400
    except Exception:
        return jsonify({"error": "invalid weight"}), 400

    try:
        margin = float(request.args.get('margin', 5))
    except Exception:
        margin = 5.0

    person = request.args.get('person', None)
    csv_name = request.args.get('csv', None)

    # Répertoire des données
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    # Colonnes des capteurs
    sensor_cols = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10']
    sensor_cols_offset = ['C1_offset', 'C2_offset', 'C3_offset', 'C4_offset', 
                          'C5_offset', 'C6_offset', 'C7_offset', 'C8_offset', 
                          'C9_offset', 'C10_offset']
    
    sums = [0.0] * 10
    count = 0
    low = w - margin
    high = w + margin

    if not os.path.isdir(data_dir):
        return jsonify({"error": f"data directory '{data_dir}' not found"}), 500

    # Construire la liste des fichiers à scanner
    files_to_scan = []
    
    if csv_name:
        safe_name = os.path.basename(csv_name)
        path = os.path.join(data_dir, safe_name)
        if os.path.exists(path):
            files_to_scan = [path]
        else:
            return jsonify({"error": f"csv '{safe_name}' not found in data directory"}), 400
    else:
        # Par défaut, utiliser le fichier principal de features
        default_files = ['02_df_preprocessing.csv', '04_df_feature.csv', '05_df_feature_final.csv']
        for f in default_files:
            path = os.path.join(data_dir, f)
            if os.path.exists(path):
                files_to_scan.append(path)
                break
        
        # Si aucun des fichiers par défaut n'existe, scanner tous les CSV
        if not files_to_scan:
            for file in os.listdir(data_dir):
                if file.endswith('.csv'):
                    files_to_scan.append(os.path.join(data_dir, file))

    print(f"📂 Scanning {len(files_to_scan)} CSV files")

    for path in files_to_scan:
        fname = os.path.basename(path)
        print(f"  📄 Reading: {fname}")
        
        try:
            df = pd.read_csv(path)
            
            # Déterminer quelles colonnes de capteurs sont présentes
            use_offset = False
            if all(col in df.columns for col in sensor_cols_offset):
                cols = sensor_cols_offset
                use_offset = True
            elif all(col in df.columns for col in sensor_cols):
                cols = sensor_cols
            else:
                print(f"    ⚠️ No sensor columns found in {fname}, skipping")
                continue
            
            # Déterminer la colonne de poids
            weight_col = None
            for possible_col in ['weight_gt', 'Weight', 'weight', 'poids', 'Poids', 'Real_weight']:
                if possible_col in df.columns:
                    weight_col = possible_col
                    break
            
            if weight_col is None:
                print(f"    ⚠️ No weight column found in {fname}, skipping")
                continue
            
            # Filtrer par poids
            df_filtered = df[
                (df[weight_col] >= low) & 
                (df[weight_col] <= high)
            ].copy()
            
            # Filtrer par personne si spécifié
            if person and len(df_filtered) > 0:
                person_cols = ['ID', 'person', 'name', 'person_name', 'Person', 'Name', 'person_id']
                person_col_found = None
                for pc in person_cols:
                    if pc in df.columns:
                        person_col_found = pc
                        break
                
                if person_col_found:
                    df_filtered = df_filtered[df_filtered[person_col_found].astype(str).str.lower() == person.lower()]
            
            if len(df_filtered) == 0:
                print(f"    ℹ️ No rows in weight range [{low}, {high}] in {fname}")
                continue
            
            # Accumuler les valeurs des capteurs
            for _, row in df_filtered.iterrows():
                vals = []
                ok = True
                for col in cols:
                    try:
                        v = float(row[col])
                        vals.append(v)
                    except (ValueError, TypeError):
                        ok = False
                        break
                
                if ok:
                    for i, v in enumerate(vals):
                        sums[i] += v
                    count += 1
            
            print(f"    ✅ Added {len(df_filtered)} rows from {fname}")
            
        except Exception as e:
            print(f"    ❌ Error reading {fname}: {e}")
            import traceback
            traceback.print_exc()
            continue

    if count == 0:
        return jsonify({
            "mean": [0] * 10,
            "n": 0,
            "message": f"No data found for weight {w} ± {margin} kg"
        }), 200

    # Calculer les moyennes
    means = [s / count for s in sums]
    
    # Normaliser comme attendu par le frontend (division par 1000)
    means_scaled = [m / 1000.0 for m in means]
    
    print(f"✅ Found {count} samples")
    print(f"   Mean values: {[round(m, 2) for m in means_scaled]}")
    
    return jsonify({
        "mean": means_scaled,
        "n": count,
        "weight_range": [low, high]
    })

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