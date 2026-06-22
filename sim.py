"""
tcp_simulator.py
────────────────
Simule le siège réel en lisant un CSV frame par frame
et en envoyant chaque frame via TCP au format JSON attendu par AIOHandler.

Usage :
    python tcp_simulator.py --csv data/person_01.csv \
                            --host 127.0.0.1 \
                            --port 5005 \
                            --fps 2          # frames par seconde
                            --weight 72      # (optionnel) poids réel pour vérification
"""

import argparse
import json
import socket
import time
import sys
import pandas as pd
import numpy as np


# ══════════════════════════════════════════════════════════════
# CONFIG PAR DÉFAUT
# ══════════════════════════════════════════════════════════════
DEFAULT_HOST  = "0.0.0.0"
DEFAULT_PORT  = 5001
DEFAULT_FPS   = 2      # 2 frames/seconde — ajustable
SENSOR_COLS   = [f"C{i}" for i in range(1, 11)]


# ══════════════════════════════════════════════════════════════
# LIRE LE CSV
# ══════════════════════════════════════════════════════════════
def load_csv(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    # Vérifier que les colonnes capteurs existent
    missing = [c for c in SENSOR_COLS if c not in df.columns]
    if missing:
        print(f"❌ Colonnes manquantes dans le CSV : {missing}")
        print(f"   Colonnes disponibles : {list(df.columns)}")
        sys.exit(1)

    print(f"✅ CSV chargé : {len(df)} frames | colonnes : {list(df.columns)}")
    return df


# ══════════════════════════════════════════════════════════════
# CONSTRUIRE LE JSON D'UNE FRAME
# ══════════════════════════════════════════════════════════════
def frame_to_json(row: pd.Series, frame_idx: int) -> str:
    """
    Construit le JSON exactement comme le vrai siège l'envoie :
    { "offset": [C1, C2, ..., C10, 0, 0, ...] }
    """
    values = [float(row[col]) for col in SENSOR_COLS]

    payload = {
        "offset"     : values,   # les 10 valeurs capteurs
        "frame_index": frame_idx
    }
    return json.dumps(payload)


# ══════════════════════════════════════════════════════════════
# PHASES ODS — simuler assis / vide
# ══════════════════════════════════════════════════════════════
def make_empty_frame_json(frame_idx: int) -> str:
    """Envoie une frame avec tous les capteurs à 0 → ODS = 0 (siège vide)."""
    payload = {
        "offset"     : [0.0] * 10,
        "frame_index": frame_idx
    }
    return json.dumps(payload)


# ══════════════════════════════════════════════════════════════
# SERVEUR TCP
# ══════════════════════════════════════════════════════════════
def run_server(df: pd.DataFrame, host: str, port: int,
               fps: float, true_weight: float = None,
               empty_frames: int = 5,
               delay_frames: int = 6):
    """
    Lance un serveur TCP et attend la connexion du client (AIOHandler).

    Scénario envoyé :
        1. [empty_frames]  frames vides  → ODS = 0 (siège vide)
        2. [delay_frames]  frames réelles → ODS = 1 MAIS dans le délai 2s
        3. [toutes les frames du CSV] → prédiction active
    """
    interval = 1.0 / fps

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(1)

    print(f"\n{'='*60}")
    print(f"  🖥️  TCP SIMULATOR READY")
    print(f"  Host    : {host}:{port}")
    print(f"  CSV     : {len(df)} frames")
    print(f"  FPS     : {fps}")
    print(f"  Délai   : {interval:.2f}s entre frames")
    if true_weight:
        print(f"  Poids réel : {true_weight} kg  (référence)")
    print(f"{'='*60}")
    print(f"\n⏳ En attente de connexion du client AIOHandler...\n")

    conn, addr = server_sock.accept()
    print(f"✅ Client connecté : {addr}\n")

    frame_idx = 0

    try:
        # ── Phase 1 : frames vides (ODS = 0) ─────────────────
        print(f"📤 Phase 1 : {empty_frames} frames VIDES (ODS=0)...")
        for _ in range(empty_frames):
            msg = make_empty_frame_json(frame_idx) + "\n"
            conn.sendall(msg.encode("utf-8"))
            print(f"   [Frame {frame_idx:03d}] VIDE envoyée")
            frame_idx += 1
            time.sleep(interval)

        # ── Phase 2 : frames dans le délai 2s (ignorées) ─────
        print(f"\n📤 Phase 2 : {delay_frames} frames dans le délai 2s (ODS=1 mais ignorées)...")
        for i in range(min(delay_frames, len(df))):
            row = df.iloc[i]
            msg = frame_to_json(row, frame_idx) + "\n"
            conn.sendall(msg.encode("utf-8"))
            cushion = sum(float(row[c]) for c in SENSOR_COLS[:6])
            print(f"   [Frame {frame_idx:03d}] cushion_sum={cushion:.0f} — dans délai")
            frame_idx += 1
            time.sleep(interval)

        # ── Phase 3 : frames actives (prédiction) ─────────────
        print(f"\n📤 Phase 3 : {len(df)} frames ACTIVES (prédiction)...")
        for i, (_, row) in enumerate(df.iterrows()):
            msg = frame_to_json(row, frame_idx) + "\n"
            conn.sendall(msg.encode("utf-8"))

            cushion = sum(float(row[c]) for c in SENSOR_COLS[:6])
            print(f"   [Frame {frame_idx:03d}] frame_active={i+1:03d}  "
                  f"cushion_sum={cushion:.0f}")

            frame_idx += 1
            time.sleep(interval)

            # Stopper après 50 frames actives (comme le client)
            if i + 1 >= 50:
                print(f"\n✅ 50 frames actives envoyées — simulation terminée")
                break

        print(f"\n{'='*60}")
        if true_weight:
            print(f"  📋 Poids réel de référence : {true_weight} kg")
        print(f"  Simulation terminée. Fermeture connexion.")
        print(f"{'='*60}\n")

    except BrokenPipeError:
        print("⚠️  Client déconnecté avant la fin.")
    except KeyboardInterrupt:
        print("\n⛔ Simulation interrompue.")
    finally:
        conn.close()
        server_sock.close()


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simulateur TCP siège — envoie un CSV frame par frame"
    )
    parser.add_argument("--csv",     required=True,              help="Chemin vers le fichier CSV")
    parser.add_argument("--host",    default=DEFAULT_HOST,       help="IP du serveur (défaut: 127.0.0.1)")
    parser.add_argument("--port",    default=DEFAULT_PORT, type=int, help="Port TCP (défaut: 5005)")
    parser.add_argument("--fps",     default=DEFAULT_FPS,  type=float, help="Frames par seconde (défaut: 2)")
    parser.add_argument("--weight",  default=None,         type=float, help="Poids réel (optionnel, pour référence)")
    parser.add_argument("--empty",   default=5,            type=int,   help="Nb frames vides au début (défaut: 5)")
    parser.add_argument("--delay",   default=6,            type=int,   help="Nb frames dans le délai 2s (défaut: 6)")

    args = parser.parse_args()

    df = load_csv(args.csv)

    run_server(
        df           = df,
        host         = args.host,
        port         = args.port,
        fps          = args.fps,
        true_weight  = args.weight,
        empty_frames = args.empty,
        delay_frames = args.delay,
    )