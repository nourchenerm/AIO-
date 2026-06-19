/**
 * socket_live.js
 * ──────────────
 * Branche SocketIO sur les charts déjà existants dans global_view.html.
 * 
 * Ajouter dans global_view.html, juste avant </body> :
 *   <script src="/socket.io/socket.io.js"></script>
 *   <script src="../static/js/socket_live.js"></script>
 *
 * Flux :
 *   csv_simulator.py → TCP → app.py → socketio.emit('frame_update') → ici
 */

(function () {

    window.socket = window.socket || io();
    const socket = window.socket;
    const predictBtn = document.getElementById('predictBtn'); // adapte l'id à ton HTML
    if (predictBtn) {
        predictBtn.addEventListener('click', function () {
            document.getElementById('spinner').style.display = 'block';
            document.getElementById('predictResults').style.display = 'none';
            socket.emit('start_prediction');  // ← déclenche aio_handler.start_prediction()
        });
    }

    /* ─── Historique pour le chart Data Analysis ─────────────────────────
       On garde les N dernières valeurs reçues.
       realWeights  : rempli par l'input "Real Weight" côté utilisateur
       datasetMeans : moyenne fixe du dataset d'entraînement (hardcodée ou
                      récupérée depuis /api/dataset_mean si tu exposes un endpoint)
       predWeights  : dernière prédiction LightGBM reçue par frame
    ──────────────────────────────────────────────────────────────────────── */
    const MAX_PTS    = 20;
    const sensors_history = Array.from({length: 10}, () => []);  // C1..C10
    const pred_history    = [];   // prédictions frame par frame (meilleur modèle)

    /* Moyenne dataset par défaut — remplace par ta vraie valeur si dispo */
    const DATASET_MEAN = 70.0;

    // Buffer for analysis during a prediction session
    window.__predict_collecting = false;
    window.__predict_sensor_buffer = [];

    /* ─── frame_update : reçu à chaque frame après délai 2s ─────────────
       d = {
         person_id, frame_idx,
         sensors: [C1..C10],
         preds:   { LightGBM: 72.3, SVR: 69.1, ... },
         ods: 1,
         cushion_sum: 48320
       }
    ──────────────────────────────────────────────────────────────────────── */
    socket.on('frame_update', function (d) {

        /* 1. Courbe capteurs — préférence: chart unique `chartSensors` affichant C1..C10 */
        if (window.chartSensors && window.chartSensors.data && window.chartSensors.data.datasets.length >= 10) {
            for (let i = 0; i < 10; i++) {
                const ds = window.chartSensors.data.datasets[i];
                if (!ds) continue;
                ds.data.push(Math.abs(d.sensors[i] / 1000));
                if (ds.data.length > MAX_PTS) ds.data.shift();
            }
            window.chartSensors.data.labels.push('');
            if (window.chartSensors.data.labels.length > MAX_PTS) window.chartSensors.data.labels.shift();
            window.chartSensors.update('none');

        } else if (window.backSensorsChart) {
            /* fallback: only update backSensorsChart (C7..C10) if present */
            const bc = window.backSensorsChart;
            /* datasets[0]=C7, [1]=C8, [2]=C9, [3]=C10 */
            const backIdx = [6, 7, 8, 9];
            backIdx.forEach(function (si, di) {
                bc.data.datasets[di].data.push(d.sensors[si]);
                if (bc.data.datasets[di].data.length > MAX_PTS)
                    bc.data.datasets[di].data.shift();
            });
            bc.data.labels.push('');
            if (bc.data.labels.length > MAX_PTS) bc.data.labels.shift();
            bc.update('none');
        }

        /* 2. Analysis collection: if a prediction is ongoing, collect sensor frames
           We'll aggregate these on `predict_result` to compute per-sensor means. */
        if (window.__predict_collecting) {
            // push raw sensors (not scaled) for accuracy
            window.__predict_sensor_buffer.push(d.sensors.slice(0, 10));
            // cap buffer length
            if (window.__predict_sensor_buffer.length > 1000) {
                window.__predict_sensor_buffer.shift();
            }
        }

        /* 3. Statut ODS */
        _setOds(1, d.cushion_sum);

        /* 4. Compteur frame */
        const fc = document.querySelector('.frame-counter');
        if (fc) fc.textContent = 'Frame #' + d.frame_idx;
    });

    /* ─── ods_update : siège vide ────────────────────────────────────── */
    socket.on('ods_update', function (d) {
        _setOds(0, d.cushion_sum);
    });

    /* ─── new_person : reset ─────────────────────────────────────────── */
    socket.on('new_person', function (d) {
        pred_history.length = 0;
        if (window.updateAnalysisChart) window.updateAnalysisChart([], []);
        console.log('👤 Nouvelle personne :', d.person_id);
    });
    socket.on('predict_error', function(d) {
        console.warn('Predict error:', d.message);
        document.getElementById('spinner').style.display = 'none';
        alert(d.message || 'Prediction error');
    });
    socket.on('predict_result', function(data) {
        console.log('predict_result received:', data);

        document.getElementById('spinner').style.display = 'none';

        var tbody = document.getElementById('predictTableBody');
        tbody.innerHTML = '';

        (data.results || []).forEach(function(row) {

            var error = Math.abs(
                parseFloat(row.predicted) - (window.currentRealWeight || 0)
            ).toFixed(1);

            tbody.innerHTML +=
                '<tr>' +
                '<td>' + row.model + '</td>' +
                '<td class="td-weight">' + parseFloat(row.predicted).toFixed(1) + ' kg</td>' +
                '<td>' + error + ' kg</td>' +
                '</tr>';
        });

        document.getElementById('predictResults').style.display = 'block';
        // Stop collecting and compute analysis chart data
        try {
            window.__predict_collecting = false;
            const buf = window.__predict_sensor_buffer || [];
            let meanSensors = [];
            if (buf.length > 0) {
                for (let i = 0; i < 10; i++) {
                    let s = 0;
                    for (let r = 0; r < buf.length; r++) s += (buf[r][i] || 0);
                    meanSensors.push(s / buf.length / 1000.0); // scale like chart ( /1000 )
                }
            } else {
                // fallback: use last frame from global chartSensors datasets
                if (window.chartSensors && window.chartSensors.data && window.chartSensors.data.datasets.length >= 10) {
                    for (let i = 0; i < 10; i++) {
                        const ds = window.chartSensors.data.datasets[i];
                        const last = ds && ds.data.length ? ds.data[ds.data.length - 1] : 0;
                        meanSensors.push(last);
                    }
                } else {
                    meanSensors = Array(10).fill(DATASET_MEAN);
                }
            }

            // Fetch dataset zone mean from backend using the real weight (if provided)
            (async function() {
                let datasetMeanSensors = Array(10).fill(DATASET_MEAN);
                try {
                    const realW = window.currentRealWeight || null;
                    if (realW) {
                        const resp = await fetch('/api/dataset_zone_mean?weight=' + encodeURIComponent(realW) + '&margin=5');
                        if (resp.ok) {
                            const body = await resp.json();
                            if (body && body.mean && Array.isArray(body.mean) && body.mean.length === 10) {
                                datasetMeanSensors = body.mean;
                            }
                        }
                    } else if (window.meanD && window.meanD.length === 10) {
                        datasetMeanSensors = window.meanD;
                    }
                } catch (e) {
                    console.warn('Failed to fetch dataset zone mean:', e);
                }

                if (window.updateAnalysisChart) window.updateAnalysisChart(meanSensors, datasetMeanSensors);
            })();
        } catch (e) {
            console.warn('Error building analysis chart from predict_result:', e);
        }
});
    socket.on('predict_progress', function(data) {

        console.log(
            'Progression : ' +
            data.frame +
            '/' +
            data.total
        );

    });

    /* ─── class_update : classifier per-frame predictions ────────── */
    socket.on('class_update', function(d) {
        console.log('class_update:', d);
        // Optionally display in UI if element exists
        try {
            var el = document.getElementById('classifierResult');
            if (el) {
                var txt = 'Class: ' + d.class;
                if (d.prob) txt += ' (' + (d.prob * 100).toFixed(0) + '%)';
                el.textContent = txt;
            }
        } catch (e) {
            // ignore
        }
    });

    /* ─── Helper ODS status ───────────────────────────────────────────── */
    function _setOds(ods, cushionSum) {
        const msgEl = document.querySelector('.status-message');
        const dotEl = document.querySelector('.status');
        if (!msgEl) return;
        if (ods === 1) {
            msgEl.textContent = 'Seat Occupied';
            dotEl.classList.remove('inactive_seat');
            dotEl.classList.add('active_seat');
        } else {
            msgEl.textContent = 'Seat is Empty';
            dotEl.classList.remove('active_seat');
            dotEl.classList.add('inactive_seat');
        }
    }

})();