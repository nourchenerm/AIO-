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

    const socket = window.socket;

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

        /* 1. Courbe Back Sensors (C7-C10) — chart existant backSensorsChart */
        if (window.backSensorsChart) {
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

        /* 2. Courbe Data Analysis — chart existant weightAnalysisChart
              On utilise le poids réel saisi dans l'input, la moyenne
              dataset fixe, et la prédiction LightGBM de cette frame.    */
        const realW = parseFloat(
            (document.getElementById('realWeightInput') || {}).value
        ) || null;

        const bestPred = d.preds['LightGBM']
                      || d.preds[Object.keys(d.preds)[0]]
                      || null;

        if (realW && bestPred !== null && window.updateAnalysisChart) {
            pred_history.push(bestPred);
            if (pred_history.length > MAX_PTS) pred_history.shift();

            const n        = pred_history.length;
            const realArr  = Array(n).fill(realW);
            const meanArr  = Array(n).fill(DATASET_MEAN);
            window.updateAnalysisChart(realArr, meanArr, pred_history);
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
        if (window.updateAnalysisChart) window.updateAnalysisChart([], [], []);
        console.log('👤 Nouvelle personne :', d.person_id);
    });
    socket.on('predict_result', function(data) {

        document.getElementById('spinner').style.display = 'none';

        var tbody = document.getElementById('predictTableBody');
        tbody.innerHTML = '';

        data.results.forEach(function(row) {

            var error = Math.abs(
                parseFloat(row.predicted) - window.currentRealWeight
            ).toFixed(1);

            tbody.innerHTML +=
                '<tr>' +
                '<td>' + row.model + '</td>' +
                '<td class="td-weight">' + parseFloat(row.predicted).toFixed(1) + ' kg</td>' +
                '<td>' + error + ' kg</td>' +
                '</tr>';
        });

        document.getElementById('predictResults').style.display = 'block';
});
    socket.on('predict_progress', function(data) {

        console.log(
            'Progression : ' +
            data.frame +
            '/' +
            data.total
        );

    });

    /* ─── Helper ODS status ───────────────────────────────────────────── */
    function _setOds(ods, cushionSum) {
        const msgEl = document.querySelector('.status-message');
        const dotEl = document.querySelector('.status');
        if (!msgEl) return;
        if (ods === 1) {
            msgEl.textContent = 'Seat Occupied';
            if (dotEl) { dotEl.className = 'status'; }
        } else {
            msgEl.textContent = 'Seat is Empty';
            if (dotEl) { dotEl.className = 'status inactive_seat'; }
        }
    }

})();