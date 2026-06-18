import json
import logging
import time
import sys
import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from scipy.stats import trim_mean, entropy

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from network.protocol_factory import ProtocolFactory


def _entropy(row):
    """Calcule l'entropie Shannon robuste."""
    v = np.clip(row, 0, None)
    t = v.sum()
    if t == 0:
        return 0.0
    p = v / t
    p = p[p > 0]
    return float(entropy(p))


def _gini(row):
    """Calcule le coefficient de Gini robuste."""
    v = np.sort(np.clip(row, 0, None))
    n = len(v)
    t = v.sum()
    if t == 0:
        return 0.0
    return float((2 * np.sum(np.cumsum(v)) - (n + 1) * t) / (n * t))


# ══════════════════════════════════════════════════════════════
# 1. LIRE LES DONNÉES DU SIÈGE
# ══════════════════════════════════════════════════════════════
def save_frame_to_csv(person_id: str, frame_idx: int, raw: np.ndarray,
                       preds: dict, output_dir: str = "test_sessions"):
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{person_id}.csv")

    row = {"person_id": person_id, "frame_idx": frame_idx}
    for i, val in enumerate(raw.flatten()[:10]):
        row[f"C{i + 1}"] = round(float(val), 2)
    for model_name, pred in preds.items():
        row[f"pred_{model_name}"] = pred

    df_row = pd.DataFrame([row])
    write_header = not os.path.exists(filepath)
    df_row.to_csv(filepath, mode='a', header=write_header, index=False)


def start_keyboard_listener(callback):
    import threading

    def listen():
        print("\n💡 Appuie sur [N] + Entrée pour enregistrer une nouvelle personne (mode terminal)\n")
        while True:
            try:
                key = input().strip().lower()
                if key == 'n':
                    callback()
            except EOFError:
                break
    t = threading.Thread(target=listen, daemon=True)
    t.start()


def predict_all_models(X: np.ndarray, models: dict) -> dict:
    predictions = {}
    for model_name, model in models.items():
        try:
            pred_frames = model.predict(X)
            pred_final = float(trim_mean(pred_frames, proportiontocut=0.1))
            predictions[model_name] = round(pred_final, 1)
        except Exception as e:
            print(f"  ⚠️  Erreur prédiction {model_name} : {e}")
            predictions[model_name] = None
    return predictions


def read_seat_data(source) -> np.ndarray:
    """
    Lit les données brutes du siège.
    source : peut être un fichier CSV, un port série, un dict, un array, etc.
    Retourne un array (N_frames, 10) — une ligne par frame, 10 capteurs.
    """
    if isinstance(source, str) and source.endswith('.csv'):
        df = pd.read_csv(source)
        raw = df[['C1', 'C2', 'C3', 'C4', 'C5',
                   'C6', 'C7', 'C8', 'C9', 'C10']].values

    elif isinstance(source, dict):
        if "offset" in source:
            raw = np.array([source["offset"][:10]])
        else:
            raw = np.array([[source.get(f'C{i}', 0) for i in range(1, 11)]])

    elif isinstance(source, (np.ndarray, list)):
        raw = np.array(source)
        if raw.ndim == 1:
            raw = raw.reshape(1, -1)

    else:
        raise ValueError(f"Source non supportée : {type(source)}")

    print(f"✅ Données lues : {raw.shape[0]} frames, {raw.shape[1]} capteurs")
    return raw.astype(np.float32)


# ══════════════════════════════════════════════════════════════
# 1.5 DÉTECTEUR ODS AVEC DÉLAI 2S
# ══════════════════════════════════════════════════════════════
def detect_ods(raw: np.ndarray, cushion_threshold: float = 20000.0) -> tuple:
    """
    Détecte ODS (Occupant Detection System).
    Si ODS=0: siège vide, pas de prédiction
    Si ODS=1: siège occupé
    """
    CUSHION_INDICES = [0, 1, 2, 3, 4, 5]  # C1-C6
    cushion_sum = raw[:, CUSHION_INDICES].sum()
    ods_status = 1 if cushion_sum > cushion_threshold else 0
    return ods_status, cushion_sum


def preprocess(raw: np.ndarray) -> np.ndarray:
    """
    Prend le raw (N_frames, 10) et retourne X (N_frames, 22)
    avec exactement les mêmes features que l'entraînement.
    """
    SENSORS = [f'C{i}_offset' for i in range(1, 11)]
    epsilon = 1e-5

    df = pd.DataFrame(raw, columns=SENSORS)

    sensor_coords = {
        'C1_offset': (-1.0, -0.5),
        'C2_offset': (1.0, -0.5),
        'C3_offset': (0.0, 0.0),
        'C4_offset': (-0.5, 0.2),
        'C5_offset': (0.5, 0.2),
        'C6_offset': (0.0, 0.8),
        'C7_offset': (0.0, 1.0),
        'C8_offset': (0.5, 1.5),
        'C9_offset': (-0.5, 1.5),
        'C10_offset': (0.0, 2.0),
    }

    CUSHION = ['C1_offset', 'C2_offset', 'C3_offset', 'C4_offset', 'C5_offset', 'C6_offset']
    BACK = ['C7_offset', 'C8_offset', 'C9_offset', 'C10_offset']
    LEFT = ['C1_offset', 'C4_offset', 'C9_offset']
    RIGHT = ['C2_offset', 'C5_offset', 'C8_offset']

    total = df[SENSORS].sum(axis=1).replace(0, np.nan)

    df['total_pressure'] = df[SENSORS].sum(axis=1)
    df['cushion_pressure'] = df[CUSHION].sum(axis=1)
    df['back_pressure'] = df[BACK].sum(axis=1)
    df['left_pressure'] = df[LEFT].sum(axis=1)
    df['right_pressure'] = df[RIGHT].sum(axis=1)

    threshold = total * 0.05
    df["active_sensors_adaptive"] = (df[SENSORS].gt(threshold, axis=0)).sum(axis=1)

    df['kurt_offsets'] = df[SENSORS].kurt(axis=1)
    df['pressure_entropy'] = df[SENSORS].apply(_entropy, axis=1)
    df['gini_pressure'] = df[SENSORS].apply(_gini, axis=1)

    df['cog_x'] = sum(
        df[s] * sensor_coords[s][0] for s in SENSORS
    ) / (total + epsilon)

    df['cog_y'] = sum(
        df[s] * sensor_coords[s][1] for s in SENSORS
    ) / (total + epsilon)

    df['lr_asymmetry'] = (
        df[LEFT].sum(axis=1) - df[RIGHT].sum(axis=1)
    ) / (total + epsilon)

    FEAT_REG = (SENSORS +
                ['total_pressure', 'cushion_pressure', 'back_pressure',
                 'left_pressure', 'right_pressure', 'active_sensors_adaptive',
                 'kurt_offsets', 'pressure_entropy', 'gini_pressure',
                 'lr_asymmetry', 'cog_x', 'cog_y'])

    X = df[FEAT_REG].values.astype(np.float32)

    return X


def predict_weight(X: np.ndarray, model_path: str = '') -> float:
    """Charge le modèle exporté et prédit le poids (utilitaire autonome, conservé pour compatibilité)."""
    try:
        model = joblib.load(model_path)
        pred_frames = model.predict(X)
        pred_final = trim_mean(pred_frames, proportiontocut=0.1)
        print(f"✅ Poids estimé : {pred_final:.1f} kg") 
        return round(pred_final, 1)
    except FileNotFoundError:
        print(f" Erreur : Le modèle '{model_path}' non trouvé")
        return None
    except Exception as e:
        print(f" Erreur lors de la prédiction : {e}")
        return None


class AIOHandler:
    """Handler for AIO (Analog Input/Output) data processing from TCP, relié au frontend via SocketIO."""

    PREDICT_TARGET_FRAMES = 100  # nombre de frames à accumuler avant la moyenne finale

    def __init__(self, config, model_paths: dict, socketio):
        """
        model_paths : dict { 'LightGBM': 'lightgbm_final.pkl', 'SVR': 'svr_final.pkl' }
        socketio    : instance flask_socketio.SocketIO utilisée pour pousser les données au frontend
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.output_dir = "test_sessions"
        self.socketio = socketio

        # ── Charger tous les modèles ──────────────────────────────
        self.models = {}
        for name, path in model_paths.items():
            try:
                self.models[name] = joblib.load(path)
                print(f"  ✅ Modèle chargé : {name} ({path})")
            except FileNotFoundError:
                print(f"  ❌ Modèle introuvable : {name} ({path})")

        # ── Gestion personnes ─────────────────────────────────────
        self.person_counter = 0
        self.current_person = None
        self.frame_count = 0

        # ── ODS state machine ─────────────────────────────────────
        self.ods_state = 0
        self.ods_detection_time = None
        self.delay_duration = 2.0

        # ── État de prédiction (déclenché par le bouton frontend) ──
        self.is_predicting = False
        self.predict_frame_count = 0
        self.predict_buffer = {}

        self._new_person()

        # ── Baseline "emptyValues" attendue par global_view.js ─────
        if self.socketio:
            self.socketio.emit('emptyValues', "0;0;0;0;0;0;0;0;0;0")

        # ── Protocol réseau ───────────────────────────────────────
        #self.aio_protocol = ProtocolFactory.create_instance(config.get('aio_protocol'))
        #self.aio_protocol.start()
        self.socketio = socketio

    # ──────────────────────────────────────────────────────────────
    def _new_person(self):
        self.person_counter += 1
        self.current_person = f"P{self.person_counter:03d}"
        self.frame_count = 0
        self.ods_state = 0
        self.ods_detection_time = None
        self.is_predicting = False
        self.predict_frame_count = 0
        self.predict_buffer = {name: [] for name in self.models}
        print(f"\n{'=' * 70}")
        print(f"👤 NOUVELLE PERSONNE : {self.current_person}")
        print(f"{'=' * 70}\n")

    # ──────────────────────────────────────────────────────────────
    def start_prediction(self):
        """Appelé quand le frontend clique sur 'Weight Predict'."""
        if self.ods_state == 0:
            if self.socketio:
                self.socketio.emit('predict_error', {'message': "Seat is EMPTY, can't start ASANA"})
            return
        self.is_predicting = True
        self.predict_frame_count = 0
        self.predict_buffer = {name: [] for name in self.models}
        print(f"\n🎯 Démarrage prédiction pour {self.current_person} (objectif {self.PREDICT_TARGET_FRAMES} frames)")

    # ──────────────────────────────────────────────────────────────
    def _emit_values(self, raw: np.ndarray, ods_status: int):
        """Émet l'événement 'values' attendu par global_view.js (statut + courbes)."""
        if not self.socketio:
            return
        frame = [float(v) for v in raw.flatten()[:10]]
        payload = {
            "time": datetime.now().isoformat(),
            "object_human": int(ods_status),
            "occupied_offset": frame,
            "offset": frame,
        }
        self.socketio.emit("frame_update", payload)

    # ──────────────────────────────────────────────────────────────
    def on_aio_receive(self, data):
        """
        Process incoming AIO data.
        Pipeline : ODS Detection → émission temps réel (statut + courbes) →
                   si prédiction active et délai 2s écoulé → accumulation jusqu'à 100 frames → moyenne finale
        """
        try:
            lines = data.strip().split('\n')

            for line in lines:
                line = line.strip()
                if line:
                    try:
                        parsed_data = json.loads(line)
                        self.aio_data = parsed_data
                        print(f"\n{'=' * 70}")
                        print(f"📊 Raw AIO Data Received:")
                        print(f"{json.dumps(self.aio_data['offset'][:10], indent=2)}")

                        # 1. Préparer les données
                        raw = read_seat_data(self.aio_data)

                        # 2. Détecteur ODS
                        ods_status, cushion_sum = detect_ods(raw, cushion_threshold=20000.0)

                        # 3. Toujours émettre vers le frontend (Section 1 statut + Section 2 courbes)
                        self._emit_values(raw, ods_status)

                        if ods_status == 0:
                            print(f"⚠️  Siège VIDE (ODS=0, cushion_sum={cushion_sum:.1f})")
                            if self.is_predicting and self.socketio:
                                self.socketio.emit('predict_error', {'message': 'Siège vide, prédiction annulée.'})
                            self.ods_state = 0
                            self.ods_detection_time = None
                            self.is_predicting = False

                        else:
                            print(f"✅ Siège OCCUPÉ (ODS=1, cushion_sum={cushion_sum:.1f})")

                            if self.ods_state == 0:
                                # Transition vide → occupé : démarrer délai 2s de stabilisation
                                self.ods_state = 1
                                self.ods_detection_time = time.time()

                            else:
                                elapsed = time.time() - self.ods_detection_time

                                if elapsed >= self.delay_duration and self.is_predicting:
                                    # ── Délai écoulé ET prédiction active : accumuler ──
                                    self.frame_count += 1
                                    self.predict_frame_count += 1

                                    X = preprocess(raw)
                                    preds = predict_all_models(X, self.models)
                                    payload = {
                                        "ods": ods_status,
                                        "predictions": preds,
                                        "sensors": raw.flatten().tolist()
                                    }
                                    print("EMIT VALUES -> FRONTEND")

                                    self.socketio.emit("values", payload)

                                    print(f"\n  📊 Frame {self.predict_frame_count:03d}/{self.PREDICT_TARGET_FRAMES} | {self.current_person}")
                                    for model_name, pred in preds.items():
                                        if pred is not None:
                                            self.predict_buffer.setdefault(model_name, []).append(pred)

                                    save_frame_to_csv(
                                        person_id=self.current_person,
                                        frame_idx=self.frame_count,
                                        raw=raw,
                                        preds=preds,
                                        output_dir=self.output_dir
                                    )

                                    if self.socketio:
                                        self.socketio.emit('predict_progress', {
                                            'frame': self.predict_frame_count,
                                            'total': self.PREDICT_TARGET_FRAMES
                                        })

                                    # ── 100 frames atteintes : moyenne finale (trim_mean) ──
                                    if self.predict_frame_count >= self.PREDICT_TARGET_FRAMES:
                                        results = []
                                        for model_name, buf in self.predict_buffer.items():
                                            if buf:
                                                final_val = round(trim_mean(buf, proportiontocut=0.1), 1)
                                                results.append({'model': model_name, 'predicted': final_val})

                                        print(f"\n{'★' * 70}")
                                        print(f"   PRÉDICTION FINALE — {self.current_person} ({self.PREDICT_TARGET_FRAMES} frames)")
                                        for r in results:
                                            print(f"   {r['model']:<14} → {r['predicted']:>6.1f} kg")
                                        print(f"{'★' * 70}")

                                        if self.socketio:
                                            self.socketio.emit('predict_result', {'results': results})

                                        self.is_predicting = False
                                        self.predict_frame_count = 0
                                        self.predict_buffer = {name: [] for name in self.models}
                                        self._new_person()

                        print(f"{'=' * 70}\n")
                        time.sleep(0.05)  # cadence entre frames

                    except json.JSONDecodeError as line_error:
                        print(f"Error parsing individual line: {line}, error: {line_error}")
                        continue

        except Exception as e:
            print(f"Error processing AIO data: {data}, error: {e}")

    def disconnect(self):
        """Disconnect from AIO protocol."""
        if self.aio_protocol:
            self.aio_protocol.disconnect()