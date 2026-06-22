// const host = 'http://192.168.1.8:5000/'
// GLOBAL VAR
window.socket = io();

window.timeupdate = false;
let time_update = true
var ip = location.host;
var oh_class_global = 0;
let last_human_class = 0;

// GLOBAL VAR
window.chartSensors = null;
let isTimeRefSetted = false;
let timeRef;
let duration = 10;
let valuesReceived = 0;
let acquisitions = 10;
let isPaused = false;
var btn_actived = false
var index_back = 0;
var index_cushion = 0;

// metrics values
let emptyValues = [];
let poids = [];
const OFFSETPOIDS_REF = [50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000];
let OFFSETPOIDS = [50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000];

const statusIndicator = document.querySelector('.status')
const statusMessage = document.querySelector('.status-message')
const statusMessageClassification = document.querySelector('.status-message-classification')
const asanaMessage = document.querySelector('.asana-message')
const button  = document.getElementById('button-test')

// Sensor configuration
let sensorConfig = null;
let configReady = false;
let visibleSensors = { backrest: [], cushion: [] };

// add globals for runtime maps
let OrderSensorBack = {};
let OrderSensorCushion = {};

// On DOM Loaded
window.addEventListener("DOMContentLoaded", (event) => {
    // Load sensor configuration first
    loadSensorConfig().then(() => {
        //configControls();
        initCharts();
        // build sensor maps after charts are initialized
        buildSensorMaps();
        setupSocketListeners();
    });
});

// Load sensor configuration from JSON
function loadSensorConfig() {
    return fetch('../static/config/sensors_config.json')
        .then(response => {
            if (!response.ok) throw new Error('Failed to load sensor config');
            return response.json();
        })
        .then(data => {
            sensorConfig = data;
            // Load visible sensors from config, fallback to all sensors if not specified
            if (sensorConfig.visibleSensors) {
                visibleSensors = sensorConfig.visibleSensors;
            } else {
                visibleSensors = {
                    backrest: sensorConfig.backrest_sensors || [],
                    cushion: sensorConfig.cushion_sensors || []
                };
            }
            configReady = true;
            console.log('Sensor configuration loaded:', sensorConfig);
            console.log('Visible sensors:', visibleSensors);
        })
        .catch(error => {
            console.error('Error loading sensor config:', error);
            // Use defaults if config fails to load
            sensorConfig = {
                backrest_sensors: [7, 8, 9, 10],
                cushion_sensors: [1, 2, 3, 4, 5, 6],
                sensor_mapping: {},
                sensor_info: {}
            };
            visibleSensors = {
                backrest: [7, 8, 9, 10],
                cushion: [1, 2, 3, 4, 5, 6]
            };
            configReady = true;
        });
}

// Build helper mapping objects from config for chart indexing
function buildSensorMaps() {
    let allDatasets = [];
    let sensorOrder = [];

    Object.keys(sensorConfig.sensor_info).forEach(idStr => {
        const id = Number(idStr);
        const info = sensorConfig.sensor_info[idStr];

        const isVisible =
            (info.type === 'backrest' && visibleSensors.backrest.includes(id)) ||
            (info.type === 'cushion' && visibleSensors.cushion.includes(id));

        if (!isVisible) return;

        allDatasets.push({
            label: info.name || `Sensor ${id}`,
            borderColor: info.color || 'black',
            data: []
        });

        sensorOrder.push(id);
    });

    if (!window.chartSensors) {
        console.warn('buildSensorMaps: chartSensors not initialized yet, skipping');
        return;
    }

    window.chartSensors.data.datasets = allDatasets;
    window.chartSensors.update();
    }

// Get actual sensor index from sensor ID
function getSensorIndex(sensorId) {
    if (sensorConfig && sensorConfig.sensor_mapping) {
        return sensorConfig.sensor_mapping[sensorId.toString()] || sensorId;
    }
    return sensorId;
}

// Check if sensor is backrest
function isBackrestSensor(sensorId) {
    if (sensorConfig && sensorConfig.backrest_sensors) {
        return sensorConfig.backrest_sensors.includes(sensorId);
    }
    return [7, 8, 9, 10].includes(sensorId);
}

// Check if sensor is cushion
function isCushionSensor(sensorId) {
    if (sensorConfig && sensorConfig.cushion_sensors) {
        return sensorConfig.cushion_sensors.includes(sensorId);
    }
    return [1, 2, 3, 4, 5, 6].includes(sensorId);
}

// Setup socket listeners
function setupSocketListeners() {
    window.socket.on('emptyValues', newEmptyValues => {
        patchEmptyValues(adpaterData('emptyValues', newEmptyValues));
    });

    window.socket.on('values', result => {
        if (!result || !emptyValues.length) return;

        const json_data = typeof result === 'string'
            ? JSON.parse(result)
            : result;
        console.log('   - offset values:', json_data.offset);

        if (!isTimeRefSetted) {
            timeRef = toTimestamp(json_data.time);
            isTimeRefSetted = true;
        }

        if ((last_human_class != json_data.object_human) && (json_data.state === 1) ) {
            last_human_class = json_data.object_human;
            if (json_data.object_human != 0) {
                json_data.occupied_offset.forEach((element, i) => {
                    OFFSETPOIDS[i] = element * 1.3;
                });
            } else {	
                OFFSETPOIDS = [...OFFSETPOIDS_REF];
            }
            calculatePoids();
        }

        if (json_data.object_human === 0) {
            statusMessageClassification.innerHTML = "";
            statusMessage.innerHTML = "Seat is empty"
            statusIndicator.classList.remove('active_seat')
            statusIndicator.classList.add('inactive_seat')
            
            const morphoSection = document.getElementById('morphoSection');
            if (morphoSection) {
                morphoSection.style.display = 'none';
            }
            btn_actived = false
        } else {
            statusMessage.innerHTML = "Seat is occupied"
            statusIndicator.classList.remove('inactive_seat')
            statusIndicator.classList.add('active_seat')
            
            const morphoSection = document.getElementById('morphoSection');
            if (morphoSection) {
                morphoSection.style.display = 'block';
            }
            
            switch (json_data.human_class) {
                case 0: statusMessageClassification.innerHTML = "EMPTY"; break;
                case 1: statusMessageClassification.innerHTML = "CHILD"; break;
                case 2: statusMessageClassification.innerHTML = "PERC_5"; break;
                case 3: statusMessageClassification.innerHTML = "PERC_50"; break;
                case 4: statusMessageClassification.innerHTML = "Large"; break;
                case 5: statusMessageClassification.innerHTML = ""; break;
                default: statusMessageClassification.innerHTML = ""; break;
            }
            
            const weightEl = document.getElementById('weight');
            if (weightEl) weightEl.innerHTML = json_data.seat_occupant_weight + "kg";
            
            const heightEl = document.getElementById('height');
            if (heightEl) heightEl.innerHTML = json_data.seat_occupant_height + "cm";
            
            const hipCircEl = document.getElementById('Hip_circ');
            if (hipCircEl) hipCircEl.innerHTML = json_data.seat_hip_width + "cm";
            
            const hipClassEl = document.getElementById('Hip_class');
            if (hipClassEl) {
                switch(json_data.seat_hip_class) {
                    case 1: hipClassEl.innerHTML = "XS"; break;
                    case 2: hipClassEl.innerHTML = "S"; break;
                    case 3: hipClassEl.innerHTML = "M"; break;
                    case 4: hipClassEl.innerHTML = "L"; break;
                    case 5: hipClassEl.innerHTML = "XL"; break;
                    default: hipClassEl.innerHTML = "NC"; break;
                }
            }
        }

        if (json_data.rtm_status === 0) {
            btn_actived = false
            $('#fixed').hide();
            $('#thorax').hide();
            $('#pelvis').hide();
            $('#feet_on_dashboard').hide();
            $('#leaning_forward').hide();        
            
            const posEl = document.querySelector('.position');
            if (posEl) posEl.innerHTML = "";
            
            const leanEl = document.querySelector('.leaning_perc');
            if (leanEl) leanEl.innerHTML = "";
        } else if (json_data.object_human === 2) {
            const posEl = document.querySelector('.position');
            if (posEl) posEl.innerHTML = "Good posture";
            
            const leanEl = document.querySelector('.leaning_perc');
            if (leanEl) leanEl.innerHTML = "";
            
            $('#fixed').show();
            $('#thorax').hide();
            $('#pelvis').hide();
            $('#feet_on_dashboard').hide();
            $('#leaning_forward').hide();
            
            if (json_data.feet_on_dashboard_alarm === 1) {
                if (posEl) posEl.innerHTML = "Feet on dashboard";
                $('#fixed').hide();
                $('#thorax').hide();
                $('#pelvis').hide();
                $('#feet_on_dashboard').show();
                $('#leaning_forward').hide();
                if (leanEl) leanEl.innerHTML = "";
            }
            else if (json_data.pelvis_alarm === 1) {
                if (posEl) posEl.innerHTML = "Pelvis drift";
                $('#fixed').hide();
                $('#thorax').hide();
                $('#pelvis').show();
                $('#feet_on_dashboard').hide();
                $('#leaning_forward').hide();
                if (leanEl) leanEl.innerHTML = "";
            }
            else if (json_data.leaning_forward_alarm === 1) {
                if (posEl) posEl.innerHTML = "Leaning Forward";
                if (leanEl) leanEl.innerHTML = "Leaning Perc : " + json_data.leaning_forward_perc + " % ";
                $('#fixed').hide();
                $('#thorax').hide();
                $('#pelvis').hide();
                $('#feet_on_dashboard').hide();
                $('#leaning_forward').show();
            }
            else if (json_data.thorax_alarm === 1) {
                if (posEl) posEl.innerHTML = "Rounded back";
                if (leanEl) leanEl.innerHTML = "Leaning Perc : " + json_data.leaning_forward_perc + " % ";
                $('#fixed').hide();
                $('#thorax').show();
                $('#pelvis').hide();
                $('#feet_on_dashboard').hide();
                $('#leaning_forward').hide();
            }
            btn_actived = true
        } else {  
            btn_actived = false
            $('#fixed').hide();
            $('#thorax').hide();
            $('#pelvis').hide();
            $('#feet_on_dashboard').hide();
            $('#leaning_forward').hide();        
            
            const posEl = document.querySelector('.position');
            if (posEl) posEl.innerHTML = "";
            
            const leanEl = document.querySelector('.leaning_perc');
            if (leanEl) leanEl.innerHTML = "";
        }

        valuesReceived--;
        let timeLabel;

        if (valuesReceived <= acquisitions) {
            timeLabel = formatDuration(toTimestamp(json_data.time) - timeRef);
            updateChartsLabels(timeLabel);
        }

        // Build reverse mapping from data index to sensor ID
        const dataIndexToSensorId = {};
        if (sensorConfig && sensorConfig.sensor_mapping) {
            Object.keys(sensorConfig.sensor_mapping).forEach(sensorIdStr => {
                const sensorId = Number(sensorIdStr);
                const dataIndex = sensorConfig.sensor_mapping[sensorIdStr];
                dataIndexToSensorId[dataIndex] = sensorId;
            });
        }

        json_data.offset.forEach((element, dataIndex) => {
            if (valuesReceived <= acquisitions) {
                // Convert data array index to sensor ID using sensor_mapping
                const sensorId = dataIndexToSensorId[dataIndex];
                if (typeof sensorId !== 'undefined') {
                    updateChartsValues(element, sensorId);
                }
            }
        });
        index_back = 0;
        index_cushion = 0;

        if (valuesReceived <= acquisitions) {
            if (!isPaused) {
                chartSensors.update();
                chartSensors.update();
            }
            valuesReceived = 11;
        }
        oh_class_global = json_data.object_human;
    });

    //document.querySelector('.nav-monitoring').addEventListener('click', onMonitoring);
    //document.querySelector('.btn-rtm').addEventListener('click', onClickActivate);
    //document.querySelector('.popupCloseButton').addEventListener('click', onClose);

    /*window.socket.on('timeupdateDone', (values) => {
        document.querySelectorAll('.btn-update, .btn-update-spinner').forEach($elem => $elem.classList.toggle('d-none'));
        timeupdate = false;
    });*/

    window.socket.on('Notif', result => {
        const json_data = adpaterData('data', result);
        if (json_data.RTM == 1) {
            btn_actived = true;
        } else {
            btn_actived = false;
        }
    });
}

// Set emptyValues & recalc poids values
function patchEmptyValues(values) {
    emptyValues = [...values];
    poids = OFFSETPOIDS.map((offset, index) => emptyValues[index] - offset);
}

function calculatePoids() {
    poids = OFFSETPOIDS.map((offset, index) => emptyValues[index] - offset);
}

function toTimestamp(strDate){
    var datum = Date.parse(strDate);
    return datum/1000;
}

function formatCsvStr(values) {
    return values.split(';').filter(str => !!str).map(str => +str.trim())
}

function initCharts() {

    // create datasets from config (use fallback if missing)
    let backDatasets = [];
    let cushionDatasets = [];
    // Track original sensor IDs for index mapping
    let backSensorOrder = [];
    let cushionSensorOrder = [];

    if (sensorConfig && sensorConfig.sensor_info) {
        Object.keys(sensorConfig.sensor_info).forEach(idStr => {
            const id = Number(idStr);
            const info = sensorConfig.sensor_info[idStr];
            
            // Only create datasets for visible sensors
            const isBackrestVisible = info.type === 'backrest' && visibleSensors.backrest.includes(id);
            const isCushionVisible = info.type === 'cushion' && visibleSensors.cushion.includes(id);
            
            if (!isBackrestVisible && !isCushionVisible) return;
            
            const ds = {
                label: info.name || (`Sensor ${id}`),
                borderColor: info.color || 'rgba(0,0,0,1)',
                order: info.chart_index,
                data: []
            };
            
            if (info.type === 'backrest' && isBackrestVisible) {
                backDatasets.push(ds);
                backSensorOrder.push(id);
            }
            if (info.type === 'cushion' && isCushionVisible) {
                cushionDatasets.push(ds);
                cushionSensorOrder.push(id);
            }
        });
        
        // Rebuild OrderBack and OrderCushion to map sensor IDs to their new dataset positions
        OrderSensorBack = {};
        OrderSensorCushion = {};
        backSensorOrder.forEach((sensorId, newIndex) => {
            OrderSensorBack[sensorId] = newIndex;
        });
        cushionSensorOrder.forEach((sensorId, newIndex) => {
            OrderSensorCushion[sensorId] = newIndex;
        });
        
        console.log('Updated OrderSensorBack:', OrderSensorBack);
        console.log('Updated OrderSensorCushion:', OrderSensorCushion);
    } else {
        // ...existing hardcoded datasets...
        backDatasets = [{
            label: 'C7',
            borderColor: 'rgb(255, 165, 2)',
            order: 0,
            data: []
        }, {
            label: 'C8 ',
            borderColor: 'rgb(55, 66, 250)',
            order: 1,
            data: []
        }, {
            label: 'C9',
            borderColor: 'rgb(46, 213, 115)',
            order: 2,
            data: []
        }, {
            label: 'C10',
            borderColor: 'rgba(47,53,66,1.000)',
            order: 3,
            data: []
        }];

        cushionDatasets = [{
            label: 'C1 - Cushion Front Right',
            borderColor: 'rgb(0, 168, 255)',
            order: 0,
            data: []
        }, {
            label: 'C2 - Cushion bugles Left',
            borderColor: 'rgb(165, 177, 194)',
            order: 1,
            data: []
        }, {
            label: 'C3 - Cushion Rear Right',
            borderColor: 'rgb(46, 213, 115)',
            order: 2,
            data: []
        }, {
            label: 'C4 - Cushion Front Left',
            borderColor: 'rgb(235, 59, 90)',
            order: 3,
            data: []
        }, {
            label: 'C5 - Cushion Rear Left',
            borderColor: 'rgb(15, 185, 177)',
            order: 4,
            data: []
        }, {
            label: 'C6 - Cushion bugles Right',
            borderColor: 'rgb(136, 84, 208)',
            order: 5,
            data: []
        }];
    }

    var sensorsEl = document.getElementById('sensorsChart');

    if (!sensorsEl) {
        console.warn('initCharts: sensorsChart canvas not found — creating stub chartSensors');
        window.chartSensors = {
            data: { labels: [], datasets: [] },
            update: function() { /* no-op stub */ }
        };
        return;
    }

    var ctx = sensorsEl.getContext('2d');

    window.chartSensors = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            animation: { duration: 0 },
            elements: {
                point: { radius: 2 },
                line: { fill: false }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Acquisition Time' }
                },
                y: {
                    title: { display: true, text: 'Sensor Values / 1000' }
                }
            }
        }
    });

    // Combine cushion + back datasets so all 10 sensors are displayed
    const combinedDatasets = cushionDatasets.concat(backDatasets);
    window.chartSensors.data.datasets = combinedDatasets;

    // Rebuild runtime mapping from sensorId -> dataset index
    OrderSensorCushion = {};
    cushionSensorOrder.forEach((sensorId, newIndex) => {
        OrderSensorCushion[sensorId] = newIndex;
    });

    OrderSensorBack = {};
    backSensorOrder.forEach((sensorId, idx) => {
        OrderSensorBack[sensorId] = cushionDatasets.length + idx;
    });

    console.log('Final OrderSensorBack:', OrderSensorBack);
    console.log('Final OrderSensorCushion:', OrderSensorCushion);

    window.chartSensors.update();


}
function onMonitoring() {
    if (oh_class_global == 0) {
        document.getElementById('popuptText').innerHTML = 'Seat is EMPTY\n can\'t start ASANA';
        $('.hover_bkgr_fricc').show();
    } else {
        window.location.href = '/monitoring';
    }
}

function onClickActivate() {
    if (btn_actived == false) {
        if (oh_class_global == 0) {
            document.getElementById('popuptText').innerHTML = 'Seat is EMPTY\n can\'t start ASANA';
            $('.hover_bkgr_fricc').show();
        } else {	
            window.socket.emit('Activate_RTM','P1');
        }
    } else {
        window.socket.emit('Stop_RTM_global_view');
    }
}

function onClose() {
    $('.hover_bkgr_fricc').hide();
}

function lerp(start, end, t) {
    return ((1 - t) * start) + (t * end);
}

function calcLerp(ratio) {
    const rMin = 55, gMin = 255, bMin = 255;
    const rMed = 255, gMed = 178, bMed = 102;
    const rMax = 255, gMax = 0, bMax = 0;

    if (ratio <= .5) {
        const r = lerp(rMin, rMed, ratio * 2);
        const g = lerp(gMin, gMed, ratio * 2);
        const b = lerp(bMin, bMed, ratio * 2);
        return `${r}, ${g}, ${b}`;
    } else {
        const r = lerp(rMed, rMax, (ratio - .5) * 2);
        const g = lerp(gMed, gMax, (ratio - .5) * 2);
        const b = lerp(bMed, bMax, (ratio - .5) * 2);
        return `${r}, ${g}, ${b}`;
    }
}

function calcLerpWithMax(ratio, rMax, gMax, bMax) {
    const rMin = 55, gMin = 255, bMin = 255;
    const r = lerp(rMin, rMax, ratio * 1.75);
    const g = lerp(gMin, gMax, ratio * 1.75);
    const b = lerp(bMin, bMax, ratio * 1.75);
    return `rgb(${r}, ${g}, ${b})`;
}

function calcRatio(start, end, nb) {
    if (nb > start) return 0;
    else if (nb < end) return 1;
    return (start - nb) / (start - end);
}

function adpaterData(type, values) {
    try {
        let result = [];

        if (type === 'emptyValues') result = formatCsvStr(values).slice(2);
        else if (type === 'data') result = JSON.parse(values);
        else if (type === 'snapshotDone') result = formatCsvStr(values).slice();
        else throw('type is not good');

        return result;
    } catch (error) {
        console.error('ERROR FOR TYPE you have to choose between simulation, data or log', type)
    }
}

function updateChartsValues(rawValue, sensorId) {
    var value = rawValue;
    var maxChartValues = duration * acquisitions;

    // Get sensor lists from config
    var cushion_sensors = sensorConfig ? sensorConfig.cushion_sensors : [];
    var back_sensors = sensorConfig ? sensorConfig.backrest_sensors : [];

    // Use maps built from config
    var OrderBack = OrderSensorBack || {};
    var OrderCushion = OrderSensorCushion || {};
    
    // Only process visible sensors
    const isBackrestVisible = visibleSensors.backrest.includes(sensorId);
    const isCushionVisible = visibleSensors.cushion.includes(sensorId);
    if (!isBackrestVisible && !isCushionVisible) return;

    if (value <= 0) {
        value = 0;
    }

    // Check if this sensor is in backrest list and has a valid chart index
    if (back_sensors.includes(sensorId)) {
        var idx = OrderBack[sensorId];
        
        // Validate that idx exists and is within bounds
        if (typeof idx !== 'undefined' && chartSensors && chartSensors.data && chartSensors.data.datasets[idx]) {
            var chartSensorsValuesLength = chartSensors.data.datasets[idx].data.length;

            if (chartSensorsValuesLength < maxChartValues) {
                chartSensors.data.datasets[idx].data.push(Math.abs(value / 1000));
            } else {
                var overflow = chartSensorsValuesLength - maxChartValues;
                var newValuesArray = chartSensors.data.datasets[idx].data.slice(overflow + 1);
                chartSensors.data.datasets[idx].data = newValuesArray;
                chartSensors.data.datasets[idx].data.push(Math.abs(value / 1000));
            }
        } else {
            console.warn(`Backrest sensor ${sensorId} (dataset idx: ${idx}) - Chart not ready`);
        }
    }
    // Check if this sensor is in cushion list and has a valid chart index
    else if (cushion_sensors.includes(sensorId)) {
        var idx = OrderCushion[sensorId];
        
        // Validate that idx exists and is within bounds
        if (typeof idx !== 'undefined' && chartSensors && chartSensors.data && chartSensors.data.datasets[idx]) {
            var chartSensorsValuesLength = chartSensors.data.datasets[idx].data.length;

            if (chartSensorsValuesLength < maxChartValues) {
                chartSensors.data.datasets[idx].data.push(Math.abs(value / 1000));
            } else {
                var overflow = chartSensorsValuesLength - maxChartValues;
                var newValuesArray = chartSensors.data.datasets[idx].data.slice(overflow + 1);
                chartSensors.data.datasets[idx].data = newValuesArray;
                chartSensors.data.datasets[idx].data.push(Math.abs(value / 1000));
            }
        } else {
            console.warn(`Cushion sensor ${sensorId} (dataset idx: ${idx}) - Chart not ready`);
        }
    } else {
        console.warn(`Sensor ${sensorId} not found in configuration (neither backrest nor cushion)`);
    }
}

function updateChartsLabels(timeLabel) {
    var chartSensorsLabelsLength = chartSensors.data.labels.length;
    var chartSensorsLabelsLength = chartSensors.data.labels.length;

    var maxChartLabels = duration * acquisitions;

    if (chartSensorsLabelsLength < maxChartLabels) {
        chartSensors.data.labels.push(timeLabel);
    } else {
        var overflow = chartSensorsLabelsLength - maxChartLabels;
        var newLabelsArray = chartSensors.data.labels.slice(overflow + 1);
        chartSensors.data.labels = newLabelsArray;
        chartSensors.data.labels.push(timeLabel);
    }

    if (chartSensorsLabelsLength < maxChartLabels) {
        chartSensors.data.labels.push(timeLabel);
    } else {
        var overflow = chartSensorsLabelsLength - maxChartLabels;
        var newLabelsArray = chartSensors.data.labels.slice(overflow + 1);
        chartSensors.data.labels = newLabelsArray;
        chartSensors.data.labels.push(timeLabel);
    }
}

function formatDuration(ms) {
    let duration = moment.duration(ms);

    if (duration.asHours() > 1) {
        return Math.floor(duration.asHours()) + moment.utc(duration.asMilliseconds()).format(":mm:ss:SSS");
    } else {
        return moment.utc(duration.asMilliseconds()).format("mm:ss:SSS");
    }
}