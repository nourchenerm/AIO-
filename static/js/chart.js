// GLOBAL VAR
const socket = io();
let snapshoting = false;
let chartBack;
let chartCushion;
let isTimeRefSetted = false;
let timeRef;
let duration = 10;
let valuesReceived = 11;
let acquisitions = 10;
let isPaused = false;
var oh_class_global = 0;

var index_back = 0;
var index_cushion = 0;

// metrics values
let emptyValues = [];

// Sensor configuration
let sensorConfig = null;
let configReady = false;
let visibleSensors = { backrest: [], cushion: [] };

// Add global maps
let OrderSensorBack = {};
let OrderSensorCushion = {};

// On DOM Loaded
window.addEventListener("DOMContentLoaded", (event) => {
    loadSensorConfig().then(() => {
        configControls();
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

function buildSensorMaps() {
    OrderSensorBack = {};
    OrderSensorCushion = {};
    if (!sensorConfig || !sensorConfig.sensor_info) return;

    // Create mapping from sensor ID to chart array index
    Object.keys(sensorConfig.sensor_info).forEach(idStr => {
        const id = Number(idStr);
        const info = sensorConfig.sensor_info[idStr];
        if (!info || typeof info.chart_index === 'undefined') return;
        if (info.type === 'backrest') OrderSensorBack[id] = info.chart_index;
        if (info.type === 'cushion') OrderSensorCushion[id] = info.chart_index;
    });
    
    console.log('OrderSensorBack:', OrderSensorBack);
    console.log('OrderSensorCushion:', OrderSensorCushion);
}

// Setup socket listeners
function setupSocketListeners() {
    socket.on('emptyValues', newEmptyValues => {
        console.log('New empty values');
        patchEmptyValues(adpaterData('emptyValues', newEmptyValues));
    });

    socket.on('values', result => {
        if (!result || !emptyValues.length) return;

        const json_data = adpaterData('data', result);
        if (!isTimeRefSetted) {
            timeRef = toTimestamp(json_data.time);
            isTimeRefSetted = true;
            console.log('   - offset values:', json_data.offset);

            console.log("Time reference setted = " + timeRef);
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
                    // Validate sensor routing
                    const cushion_sensors = sensorConfig ? sensorConfig.cushion_sensors : [];
                    const back_sensors = sensorConfig ? sensorConfig.backrest_sensors : [];
                    const sensorType = back_sensors.includes(sensorId) ? 'backrest' : 
                                      cushion_sensors.includes(sensorId) ? 'cushion' : 'unknown';
                    
                    // Debug: Log first few values to verify correct routing
                    if (valuesReceived === acquisitions && dataIndex <= 5) {
                        console.log(`Data[${dataIndex}] → Sensor ${sensorId} (${sensorType}): ${element}`);
                    }
                    
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
}

// Set emptyValues & recalc poids values
function patchEmptyValues(values) {
    emptyValues = [...values];
}

// Adapt data provided by server
function adpaterData(type, values) {
    try {
        let result = [];

        if (type === 'emptyValues') result = formatCsvStr(values).slice(2);
        else if (type === 'data') result = JSON.parse(values);
        else if (type === 'snapshotDone') result = formatCsvStr(values).slice();
        else throw ('type is not good');

        return result;
    } catch (error) {
        console.error('ERROR FOR TYPE you have to choose between simulation, data or log', type)
    }
}

function toTimestamp(strDate) {
    var datum = Date.parse(strDate);
    return datum / 1000;
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
        // fallback to previous hardcoded datasets
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
                    //tension: 0, // disables bezier curves
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
                    //tension: 0, // disables bezier curves
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
    // chartBack.data.datasets[2].hidden = true
    //chartBack.data.datasets[3].hidden = true
    //chartBack.data.datasets[4].hidden = true
    // chartCushion.data.datasets[2].hidden = true
}

function configControls() {

    document.getElementById('duration').addEventListener('input', function () {
        duration = +this.value;
        document.getElementById('durationValue').innerHTML = this.value;
    });

    document.getElementById('acquisitions').addEventListener('input', function () {
        acquisitions = +this.value;
        document.getElementById('acquisitionsValue').innerHTML = this.value;
    });

    document.querySelector('.btn-chart-pause').addEventListener('click', onClickChartPause);
    document.querySelector('.btn-chart-resume').addEventListener('click', onClickChartResume);
    document.querySelector('.btn-chart-clear').addEventListener('click', onClickChartClear);
    document.querySelector('.btn-chart-resetZoom').addEventListener('click', onClickResetZoom);
    
    // Sensor button listeners are attached by the HTML script that generates the buttons dynamically
    // This is done to avoid race conditions and ensure buttons exist before attaching listeners
    
    document.querySelector('.nav-monitoring').addEventListener('click', onMonitoring);
    document.querySelector('.popupCloseButton').addEventListener('click', onClose);
}

// Dynamically attach listeners to sensor buttons based on configuration
function attachSensorButtonListeners() {
    if (!sensorConfig || !sensorConfig.sensor_info) return;
    
    Object.keys(sensorConfig.sensor_info).forEach(idStr => {
        const sensorId = Number(idStr);
        const info = sensorConfig.sensor_info[idStr];
        const buttonId = `btn-sensor-${sensorId}`;
        const buttonElement = document.getElementById(buttonId);
        
        if (!buttonElement) return;
        
        buttonElement.addEventListener('click', () => {
            onClickSensorToggle(sensorId, info);
        });
    });
}

// Generic sensor button click handler
function onClickSensorToggle(sensorId, sensorInfo) {
    const chartIndex = sensorInfo.chart_index;
    const isBackrest = sensorInfo.type === 'backrest';
    const chart = isBackrest ? chartBack : chartCushion;
    const buttonId = `btn-sensor-${sensorId}`;
    const buttonElement = document.getElementById(buttonId);
    
    if (!chart || !chart.data || !chart.data.datasets[chartIndex]) {
        console.warn(`Sensor ${sensorId}: Chart or dataset not found`);
        return;
    }
    
    chart.data.datasets[chartIndex].hidden = !chart.data.datasets[chartIndex].hidden;
    chart.update();
    
    const isHidden = chart.data.datasets[chartIndex].hidden;
    if (isHidden) {
        buttonElement.className = `btn-chart btn-sensor-${sensorId} btn-color-hidden`;
    } else {
        buttonElement.className = `btn-chart btn-sensor-${sensorId} btn-sensor-color`;
        buttonElement.style.backgroundColor = sensorInfo.color;
    }
}

function onClickChartPause() {
    console.log("Charts Pause");
    isPaused = true;
    chartBack.stop();
    chartCushion.stop();
    document.querySelector('.btn-chart-pause').style.display = "none";
    document.querySelector('.btn-chart-resume').style.display = "inline-block";
}

function onClickChartResume() {
    console.log("Charts Resume")
    isPaused = false;
    chartBack.render();
    chartCushion.render();
    document.querySelector('.btn-chart-resume').style.display = "none";
    document.querySelector('.btn-chart-pause').style.display = "inline-block";
}

function onClickChartClear() {
    console.log("Chart Clear")

    chartBack.data.labels = [];
    chartCushion.data.labels = [];

    chartBack.data.datasets.forEach((set, i) => {
        set.data = [];
    });
    chartCushion.data.datasets.forEach((set, i) => {
        set.data = [];
    });


    chartBack.clear();
    chartCushion.clear();
    onClickChartResume();
    chartBack.update();
    chartCushion.update();
}

function onClickResetZoom() {
    console.log("Reset Zoom");
    chartBack.resetZoom();
    chartCushion.resetZoom();
    document.querySelector('.btn-chart-resetZoom').style.display = "none";
}




function updateChartsValues(rawValue, sensorId) {

    var value = rawValue;
    var maxChartValues = duration * acquisitions;

    var cushion_sensors = sensorConfig ? sensorConfig.cushion_sensors : [];
    var back_sensors = sensorConfig ? sensorConfig.backrest_sensors : [];

    var OrderBack = OrderSensorBack || {};
    var OrderCushion = OrderSensorCushion || {};
    
    // Only process visible sensors
    const isBackrestVisible = visibleSensors.backrest.includes(sensorId);
    const isCushionVisible = visibleSensors.cushion.includes(sensorId);
    if (!isBackrestVisible && !isCushionVisible) return;

    if (value <= 0) {
        value = 0;
    }

    if (back_sensors.includes(sensorId)) {
        var idx = OrderBack[sensorId];
        
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
    else if (cushion_sensors.includes(sensorId)) {
        var idx = OrderCushion[sensorId];
        
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
        console.warn(`Sensor ${sensorId} not found in sensor configuration`);
    }
}

function updateChartsLabels(timeLabel) {

    var chartBackLabelsLength = chartBack.data.labels.length;
    var chartCushionLabelsLength = chartCushion.data.labels.length;

    var maxChartLabels = duration * acquisitions;

    if (chartBackLabelsLength < maxChartLabels)
        chartBack.data.labels.push(timeLabel);
    else {
        var overflow = chartBackLabelsLength - maxChartLabels;
        var newLabelsArray = chartBack.data.labels.slice(overflow + 1);
        chartBack.data.labels = newLabelsArray;
        chartBack.data.labels.push(timeLabel);
    }

    if (chartCushionLabelsLength < maxChartLabels)
        chartCushion.data.labels.push(timeLabel);
    else {
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

function onMonitoring() {
    if (oh_class_global == 0) {
        document.querySelector('.hover_bkgr_fricc').style.display = 'block';
    }
    else {
        window.location.href = '/monitoring';
    }
}

function onClose() {
    $('.hover_bkgr_fricc').hide();
}