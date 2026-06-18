//const host = 'http://192.168.1.8:5000/'
// GLOBAL VAR
window.socket = io();

window.timeupdate = false;
let time_update = true
var ip = location.host;
var oh_class_global = 0;
let last_human_class = 0;

// GLOBAL VAR
let chartBack;
let chartCushion;
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
            buildSensorMaps(); // create maps right after load
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
            buildSensorMaps();
        });
}

// Build helper mapping objects from config for chart indexing
function buildSensorMaps() {
    OrderSensorBack = {};
    OrderSensorCushion = {};
    if (!sensorConfig || !sensorConfig.sensor_info) return;

    Object.keys(sensorConfig.sensor_info).forEach(idStr => {
        const id = Number(idStr);
        const info = sensorConfig.sensor_info[idStr];
        if (!info) return;
        if (info.type === 'backrest') OrderSensorBack[id] = info.chart_index;
        if (info.type === 'cushion') OrderSensorCushion[id] = info.chart_index;
    });
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
    socket.on('emptyValues', newEmptyValues => {
        patchEmptyValues(adpaterData('emptyValues', newEmptyValues));
    });

    socket.on('values', result => {
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
                chartBack.update();
                chartCushion.update();
            }
            valuesReceived = 11;
        }
        oh_class_global = json_data.object_human;
    });

    //document.querySelector('.nav-monitoring').addEventListener('click', onMonitoring);
    //document.querySelector('.btn-rtm').addEventListener('click', onClickActivate);
    //document.querySelector('.popupCloseButton').addEventListener('click', onClose);

    /*socket.on('timeupdateDone', (values) => {
        document.querySelectorAll('.btn-update, .btn-update-spinner').forEach($elem => $elem.classList.toggle('d-none'));
        timeupdate = false;
    });*/

    socket.on('Notif', result => {
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
            label: 'C7 - Back Low Center',
            borderColor: 'rgb(255, 165, 2)',
            order: 0,
            data: []
        }, {
            label: 'C8 - Back Center Right',
            borderColor: 'rgb(55, 66, 250)',
            order: 1,
            data: []
        }, {
            label: 'C9 - Back Center Left',
            borderColor: 'rgb(46, 213, 115)',
            order: 2,
            data: []
        }, {
            label: 'C10 - Back High Center',
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

    var ctx = document.getElementById('backSensorsChart').getContext('2d');
    chartBack = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: backDatasets
        },
        options: {
            title: {
                display: true,
                text: 'Back Sensors',
                fontSize: 16,
                fontStyle: 'bold'
            },
            elements: {
                point: {
                    radius: 2,
                    pointStyle: 'circle',
                    borderWidth: 2
                },
                line: {
                    fill: false
                }
            },
            animation: {
                duration: 0
            },
            hover: {
                animationDuration: 0
            },
            responsiveAnimationDuration: 0,
            legend: {
                display: false,
                position: 'left',
                labels: {
                    boxWidth: 20,
                    fontSize: 14,
                    fontStyle: 'bold',
                    padding: 14
                }
            },
            scales: {
                xAxes: [{
                    type: 'category',
                    scaleLabel: {
                        display: true,
                        labelString: 'Acquisition Time',
                        fontSize: 14,
                        fontStyle: 'bold',
                        padding: 6
                    },
                    gridLines: {
                        tickMarkLength: 6
                    },
                    ticks: {
                        fontSize: 12,
                        fontStyle: 'bold',
                        padding: 6
                    }
                }],
                yAxes: [{
                    type: 'linear',
                    scaleLabel: {
                        display: true,
                        labelString: 'Back Sensors Abs Offset Values / 1000',
                        fontSize: 14,
                        fontStyle: 'bold',
                        padding: 6
                    },
                    gridLines: {
                        tickMarkLength: 6
                    },
                    ticks: {
                        fontSize: 12,
                        fontStyle: 'bold',
                        padding: 6,
                        suggestedMin: 0,
                        suggestedMax: 20
                    }
                }]
            },
            tooltips: {
                enabled: true,
                mode: 'interpolate',
                intersect: false,
                position: 'nearest',
                titleFontSize: 14,
                titleSpacing: 4,
                titleMarginBottom: 8,
                bodyFontSize: 12,
                bodyFontStyle: 'bold',
                bodySpacing: 4,
                footerMarginTop: 10,
                xPadding: 10,
                yPadding: 10
            },
            plugins: {
                crosshair: {
                    line: {
                        color: '#000',
                        width: 2
                    },
                    sync: {
                        enabled: true,
                        group: 1,
                        suppressTooltips: false
                    },
                    zoom: {
                        enabled: false
                    }
                },
                zoom: {
                    pan: {
                        enabled: true,
                        mode: 'xy'
                    },
                    zoom: {
                        enabled: true,
                        mode: 'x',
                        speed: 1000,
                        sensitivity: 0,
                        onZoom: function ({ chart }) {
                            document.querySelector('.btn-chart-resetZoom').style.display = "inline-block";
                        }
                    }
                }
            }
        }
    });

    var ctx2 = document.getElementById('cushionSensorsChart').getContext('2d');
    chartCushion = new Chart(ctx2, {
        type: 'line',
        data: {
            labels: [],
            datasets: cushionDatasets
        },
        options: {
            title: {
                display: true,
                text: 'Cushion Sensors',
                fontSize: 16,
                fontStyle: 'bold'
            },
            elements: {
                point: {
                    radius: 2,
                    pointStyle: 'circle',
                    borderWidth: 2
                },
                line: {
                    fill: false
                }
            },
            animation: {
                duration: 0
            },
            hover: {
                animationDuration: 0
            },
            responsiveAnimationDuration: 0,
            legend: {
                display: false,
                position: 'left',
                labels: {
                    boxWidth: 20,
                    fontSize: 14,
                    fontStyle: 'bold',
                    padding: 14
                }
            },
            scales: {
                xAxes: [{
                    type: 'category',
                    scaleLabel: {
                        display: true,
                        labelString: 'Acquisition Time',
                        fontSize: 14,
                        fontStyle: 'bold',
                        padding: 6
                    },
                    gridLines: {
                        tickMarkLength: 6
                    },
                    ticks: {
                        fontSize: 12,
                        fontStyle: 'bold',
                        padding: 6
                    }
                }],
                yAxes: [{
                    type: 'linear',
                    scaleLabel: {
                        display: true,
                        labelString: 'Cushion Sensors Abs Offset Values / 1000',
                        fontSize: 14,
                        fontStyle: 'bold',
                        padding: 6
                    },
                    gridLines: {
                        tickMarkLength: 6
                    },
                    ticks: {
                        fontSize: 12,
                        fontStyle: 'bold',
                        padding: 6,
                        suggestedMin: 0,
                        suggestedMax: 20
                    }
                }]
            },
            tooltips: {
                enabled: true,
                mode: 'interpolate',
                intersect: false,
                position: 'nearest',
                titleFontSize: 14,
                titleSpacing: 4,
                titleMarginBottom: 8,
                bodyFontSize: 12,
                bodyFontStyle: 'bold',
                bodySpacing: 4,
                footerMarginTop: 10,
                xPadding: 10,
                yPadding: 10
            },
            plugins: {
                crosshair: {
                    line: {
                        color: '#000',
                        width: 2
                    },
                    sync: {
                        enabled: true,
                        group: 1,
                        suppressTooltips: false
                    },
                    zoom: {
                        enabled: false
                    }
                },
                zoom: {
                    pan: {
                        enabled: true,
                        mode: 'xy',
                    },
                    zoom: {
                        enabled: true,
                        mode: 'x',
                        speed: 1000,
                        sensitivity: 0,
                        onZoom: function ({ chart }) {
                            document.querySelector('.btn-chart-resetZoom').style.display = "inline-block";
                        }
                    }
                }
            }
        }
    });
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
            socket.emit('Activate_RTM','P1');
        }
    } else {
        socket.emit('Stop_RTM_global_view');
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
        if (typeof idx !== 'undefined' && chartBack && chartBack.data && chartBack.data.datasets[idx]) {
            var chartBackValuesLength = chartBack.data.datasets[idx].data.length;

            if (chartBackValuesLength < maxChartValues) {
                chartBack.data.datasets[idx].data.push(Math.abs(value / 1000));
            } else {
                var overflow = chartBackValuesLength - maxChartValues;
                var newValuesArray = chartBack.data.datasets[idx].data.slice(overflow + 1);
                chartBack.data.datasets[idx].data = newValuesArray;
                chartBack.data.datasets[idx].data.push(Math.abs(value / 1000));
            }
        } else {
            console.warn(`Backrest sensor ${sensorId} (dataset idx: ${idx}) - Chart not ready`);
        }
    }
    // Check if this sensor is in cushion list and has a valid chart index
    else if (cushion_sensors.includes(sensorId)) {
        var idx = OrderCushion[sensorId];
        
        // Validate that idx exists and is within bounds
        if (typeof idx !== 'undefined' && chartCushion && chartCushion.data && chartCushion.data.datasets[idx]) {
            var chartCushionValuesLength = chartCushion.data.datasets[idx].data.length;

            if (chartCushionValuesLength < maxChartValues) {
                chartCushion.data.datasets[idx].data.push(Math.abs(value / 1000));
            } else {
                var overflow = chartCushionValuesLength - maxChartValues;
                var newValuesArray = chartCushion.data.datasets[idx].data.slice(overflow + 1);
                chartCushion.data.datasets[idx].data = newValuesArray;
                chartCushion.data.datasets[idx].data.push(Math.abs(value / 1000));
            }
        } else {
            console.warn(`Cushion sensor ${sensorId} (dataset idx: ${idx}) - Chart not ready`);
        }
    } else {
        console.warn(`Sensor ${sensorId} not found in configuration (neither backrest nor cushion)`);
    }
}

function updateChartsLabels(timeLabel) {
    var chartBackLabelsLength = chartBack.data.labels.length;
    var chartCushionLabelsLength = chartCushion.data.labels.length;

    var maxChartLabels = duration * acquisitions;

    if (chartBackLabelsLength < maxChartLabels) {
        chartBack.data.labels.push(timeLabel);
    } else {
        var overflow = chartBackLabelsLength - maxChartLabels;
        var newLabelsArray = chartBack.data.labels.slice(overflow + 1);
        chartBack.data.labels = newLabelsArray;
        chartBack.data.labels.push(timeLabel);
    }

    if (chartCushionLabelsLength < maxChartLabels) {
        chartCushion.data.labels.push(timeLabel);
    } else {
        var overflow = chartCushionLabelsLength - maxChartLabels;
        var newLabelsArray = chartCushion.data.labels.slice(overflow + 1);
        chartCushion.data.labels = newLabelsArray;
        chartCushion.data.labels.push(timeLabel);
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