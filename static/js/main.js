//const host = 'http://192.168.1.8:5000/'
// GLOBAL VAR
const socket = io();
let snapshoting = false;
let timeupdate = false;
let referenceupdate = false;
let debug_counter = 0;
var firstStability = 0;
let counter_3 = false;
let counter_2 = false;
let counter_1 = false;
let clicked = false;
let clicked_fidgeting = false;
let btn_actived = false;
let debug_data = true
let time_update = true
var ip = location.host;
var oh_class_global = 0;
let last_human_class = 0;


// metrics values
let emptyValues = [];
let poids = [];
//const OFFSETPOIDS_REF = [85000, 160000, 100000, 150000, 75000, 85000, 80000, 80000, 90000, 130000];
//const OFFSETPOIDS_REF =[30000, 30000, 30000, 30000, 30000, 30000, 30000, 30000, 30000, 30000];
const OFFSETPOIDS_REF = [50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000];
OFFSETPOIDS = [50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000];

// Sensor configuration (for dynamic table and mapping)
let sensorConfig = null;

// Once page DOM is ready we will fetch the config and populate table rows
function loadSensorConfig() {
    return fetch('../static/config/sensors_config.json')
        .then(resp => {
            if (!resp.ok) throw new Error('Failed to load sensor config');
            return resp.json();
        })
        .then(cfg => {
            sensorConfig = cfg;
            buildSensorTable();
        })
        .catch(err => {
            console.error('Unable to read sensor configuration', err);
            // fallback to empty config so functions below still work
            sensorConfig = { sensor_mapping: {}, sensor_info: {} };
            buildSensorTable();
        });
}

function buildSensorTable() {
    const tbody = document.getElementById('sensorTableBody');
    if (!tbody) return;

    // determine list of sensor ids to display
    let ids = [];
    if (sensorConfig && sensorConfig.sensor_mapping && Object.keys(sensorConfig.sensor_mapping).length) {
        ids = Object.keys(sensorConfig.sensor_mapping).map(Number);
    } else if (sensorConfig && sensorConfig.sensor_info) {
        ids = Object.keys(sensorConfig.sensor_info).map(Number);
    }
    ids.sort((a, b) => a - b);

    // clear existing
    tbody.innerHTML = '';

    ids.forEach(id => {
        const tr = document.createElement('tr');

        const tdName = document.createElement('td');
        tdName.textContent = `C${id}`;

        const tdRaw = document.createElement('td');
        tdRaw.setAttribute('data-value', `c${id}`);
        tdRaw.innerHTML = '<span>0</span>';

        const tdOffset = document.createElement('td');
        tdOffset.setAttribute('offset-value', `c${id}`);
        tdOffset.innerHTML = '<span>0</span>';

        tr.appendChild(tdName);
        tr.appendChild(tdRaw);
        tr.appendChild(tdOffset);

        // always include asana column on HMI page
        const tdAsana = document.createElement('td');
        tdAsana.setAttribute('offset-asana', `c${id}`);
        tdAsana.innerHTML = '<span>0</span>';
        tr.appendChild(tdAsana);

        tbody.appendChild(tr);
    });
}

// utility: given an index from server array, return sensor id using reverse mapping
function mapIndexToSensorId(index) {
    if (sensorConfig && sensorConfig.sensor_mapping) {
        for (const [key, val] of Object.entries(sensorConfig.sensor_mapping)) {
            if (val === index) {
                return Number(key);
            }
        }
    }
    // fall back to 1-based sequence
    return index + 1;
}


// On DOM Loaded
window.addEventListener("DOMContentLoaded", (event) => {
	loadSensorConfig(); // fetch sensor configuration and build the sensor table before any updates arrive

		// Event fire when empty values is emit by server (connection & change file)
		// cf : snapshot_empty_values.csv
		socket.on('emptyValues', newEmptyValues => {
			console.log('New empty values');
			patchEmptyValues(adpaterData('emptyValues', newEmptyValues));
			snapshoting = false;
		});
		
		// Event fire when values of captors is emit by server (connection & change file)
		// cf : OneLineData.csv
		socket.on('values', result => {

                const json_data = adpaterData('data', result);
			json_data.sensors.forEach((element, i) => {
				if (i<6){
					const [start, end] = [emptyValues[i], poids[i]];
					const ratio = calcRatio(start, end, element);
					const mainColor = calcLerp(ratio).split(",");

					// Calc for each 0.1 step (radius)
					let index = 1;
					let colors = [];
					while (index >= 0) {
						colors.push(calcLerpWithMax(index, ...mainColor));
						index -= 0.1;
					}

					// Apply color of looping captor : change coeff to move behavior of radius
					const indexCapteur = +(i + 1);
					const $stops = document.querySelectorAll(`[data-capteur="c${indexCapteur}"] defs radialGradient stop`);
					$stops.forEach(function ($stop, index2) {
						$stop.setAttribute('stop-color', colors[index2]);
						const radius = ratio / 2.5;
						$stop.closest('radialGradient').setAttribute('r', radius > 0.6 ? 0.6 : (radius > 0.2 ? radius : 0.2));
					});
			}
        });

        const [$pssc, psscValue] = [document.querySelector('li[data-pssc]'), json_data.init];
        const [$searchPos, searchPosValue] = [document.querySelector('li[data-search-pos]'), json_data.state];
        const typePosValue = parseInt(json_data.final_position);
        const [$seat_condition, seat_condition] = [document.querySelector('li[data-seat-condition]'), json_data.dry_flag];
        const [$ohPos, oh_class] = [document.querySelector('li[data-oh-cl]'), json_data.object_human];		
        const  $ohPosGlobal= document.querySelector('div[data-oh-global-cl]');
        //const [$humanPos, human_class] = [document.querySelector('li[human-cl-data]'), json_data.human_class];
        const [$thorax, thorax_class] = [document.querySelector('li[data-thorax]'), json_data.thorax_class];
        const [$pelvis, pelvis_class] = [document.querySelector('li[data-pelvis]'), json_data.pelvis_class];		
        const [$ex_thorax, ex_thorax_class] = [document.querySelector('li[data-extended-thorax]'), json_data.thorax_ext_class];
        const [$fidgetings, fidgetings_class] = [document.querySelector('li[data-fidgeting]'), json_data.fidgeting_class];
        const $bmi_ls = document.querySelector('li[bmi-cl]')
		const $production = document.querySelector('div[production-value]')
		
		
		
		const $humanPos = document.querySelector('li[human-cl-data]')
        const [$human_class_button, human_class] = [document.querySelector('li[data-human-cl]'), json_data.human_class];
		
		const $rtm_active = document.querySelector('button[active-cl]')
		const $rtm_is_activated = document.querySelector('button[activated-cl]')
		let rtm_actived = json_data.rtm_status;

		
		if (searchPosValue === 1) {
			firstStability = 1;
		}
	
		
		if (seat_condition === 1) {
				$seat_condition.querySelector('span').innerHTML = "DRY";				
			} else if (seat_condition === 2) {
				$seat_condition.querySelector('span').innerHTML = 'PRE_WET';
			} else if (seat_condition === 3) {
				$seat_condition.querySelector('span').innerHTML = 'WET';
			}		
		
			console.log(OFFSETPOIDS);
			console.log(last_human_class);
		if ((last_human_class != json_data.object_human) && (json_data.state === 1) ){
			last_human_class = json_data.object_human;
				if (json_data.object_human != 0) {

					json_data.offset.forEach((element, i) => {
						OFFSETPOIDS[i] = element * 1.3;
					});
				}
				else	
					OFFSETPOIDS = OFFSETPOIDS_REF;
				console.log(OFFSETPOIDS);
				console.log(last_human_class);
				calculatePoids();
		}

		oh_class_global = oh_class;
		if (oh_class === 0) {
			$ohPos.querySelector('span').innerHTML = "Empty Seat";
			$ohPosGlobal.innerHTML = "Empty Seat";			
			//$human_class_button.classList.add('d-none');			
			$rtm_active.classList.remove('d-none');
			$rtm_is_activated.classList.add('d-none');
			$human_class_button.querySelector('span').innerHTML = "Empty";
			
		} else if (oh_class === 1) {
			$ohPos.querySelector('span').innerHTML = 'Object &#x2705;';			
			$ohPosGlobal.innerHTML = 'Object &#x2705;';
			$rtm_active.classList.remove('d-none');
			$rtm_is_activated.classList.add('d-none');
			$human_class_button.querySelector('span').innerHTML = "Child Seat";
		} else if (oh_class === 2) {
			$ohPos.querySelector('span').innerHTML = 'Human &#x2705;';
			$ohPosGlobal.innerHTML ='Human &#x2705;';
			$rtm_active.classList.remove('d-none');
			$rtm_is_activated.classList.add('d-none');
			switch (human_class) {
				case 0: $human_class_button.querySelector('span').innerHTML = "Baby";
				break;
				case 1: $human_class_button.querySelector('span').innerHTML = "Child";
				break;
				case 2: $human_class_button.querySelector('span').innerHTML = "5th perc";
				break;
				case 3: $human_class_button.querySelector('span').innerHTML = "50th perc";
				break;
				case 4: $human_class_button.querySelector('span').innerHTML = "95th perc";
				break;
				case 5: $human_class_button.querySelector('span').innerHTML = "Unknown";
				break;
				default: $human_class_button.querySelector('span').innerHTML = "(not available)";
				break;
			}
			
			if (rtm_actived == true && btn_actived == true)
			{
				$rtm_active.classList.add('d-none');
				$rtm_is_activated.classList.remove('d-none');
			}
			else 
			{
				$rtm_active.classList.remove('d-none');
				$rtm_is_activated.classList.add('d-none');
				//document.querySelector('div[data-monitoring]').classList.add('d-none');
			}
			
			/*json_data.human_list.forEach((element, i) => {
				const $cell = document.querySelector(`[classic="${i}"]`);
				$cell.querySelector('span').innerHTML = Math.round((element[1] * 100)/ 1.2);
			});*/

		}

        if  (oh_class != 2 && firstStability == 1 ) {			
			firstStability = 0;			
			//document.querySelector('div[data-monitoring]').classList.add('d-none');
			btn_actived = false;		
		}

		if (debug_data == true) {
            debug_counter += 1;

			// if configuration has been loaded but the table is still empty, build it now
			if (sensorConfig && document.getElementById('sensorTableBody') && document.getElementById('sensorTableBody').children.length === 0) {
				buildSensorTable();
			}

            if (debug_counter % 4 == 0) {
                debug_counter = 0;
                json_data.avg.forEach((element, i) => {
                    // Apply color of looping captor : change coeff to move behavior of radius
                    const sensorId = mapIndexToSensorId(i);
                    const $cell = document.querySelector(`td[data-value="c${sensorId}"]`);
                    if ($cell) $cell.querySelector('span').innerHTML = element;
                });
                json_data.occupied_offset.forEach((element, i) => {
                    // Apply color of looping captor : change coeff to move behavior of radius
                    const sensorId = mapIndexToSensorId(i);
                    const $cell = document.querySelector(`td[offset-value="c${sensorId}"]`);
                    if ($cell) $cell.querySelector('span').innerHTML = element;
                });
				try {
					if (json_data.rtm_status == 1) {
						json_data.asana_offset.forEach((element, i) => {
							// Apply color of looping captor : change coeff to move behavior of radius
							const sensorId = mapIndexToSensorId(i);
							const $cell = document.querySelector(`td[offset-asana="c${sensorId}"]`);
							if ($cell) $cell.querySelector('span').innerHTML = element;
						});
					}
				} catch (error) {
					console.error('Error processing asana_offset data:', error);
				}
				}
            }
        }
		
    );

    if (debug_data == false) {
        document.querySelector('.debug').classList.add('d-none');
        console.log("Debug is hidden")
    }
    else {
        console.log("Debug is visible")
    }
    if (time_update == false) {
        document.querySelector('.btn-update').classList.add('d-none');
        console.log("System update is hidden")
    }
    else {
        console.log("System update is visible")
    }
    // Add eventlistener on snapshot btn
    document.querySelector('.btn-snapshot').addEventListener('click', onClickSnapshot);
    document.querySelector('.btn-update').addEventListener('click', onClickUpdate);
	document.querySelector('.btn-yes-production').addEventListener('click', onClickYesProduction);
	document.querySelector('.btn-no-production').addEventListener('click', onClickNoProduction);
	document.querySelector('.btn-rtm').addEventListener('click', onClickActivate);
	document.querySelector('.btn-reference').addEventListener('click', onUpdateReference);
	document.querySelector('.btn-ocs').addEventListener('click', onOCS);
	document.querySelector('.nav-monitoring').addEventListener('click', onMonitoring);
	//document.querySelector('.nav-monitoring-confort').addEventListener('click', onMonitoringConfort);
	document.querySelector('.nav-hmi').addEventListener('click', onHMI);	
	document.getElementById('btn-p1').addEventListener('click', onProfile1);
	document.getElementById('btn-p2').addEventListener('click', onProfile2);
	document.getElementById('btn-p3').addEventListener('click', onProfile3);
	document.getElementById('btn-p4').addEventListener('click', onProfile4);
	
	document.querySelector('.popupCloseButton').addEventListener('click', onClose);
    // Event fire when snapshotDone is emit by server (file[1] === 0)
    socket.on('snapshotDone', (values) => {
        console.log('snapshot done');
        document.querySelectorAll('.btn-snapshot, .btn-snapshot-spinner').forEach($elem => $elem.classList.toggle('d-none'));
        snapshoting = false;
    });

    socket.on('timeupdateDone', (values) => {
        console.log('Time update done');
        document.querySelectorAll('.btn-update, .btn-update-spinner').forEach($elem => $elem.classList.toggle('d-none'));
        timeupdate = false;
    });
	
	socket.on('UpdateReferenceDone', (values) => {
        console.log('Reference update done');
        document.querySelectorAll('.btn-reference, .btn-reference-spinner').forEach($elem => $elem.classList.toggle('d-none'));
        referenceupdate = false;
    });
		
	socket.on('Notif', result => {

        const json_data = adpaterData('data', result);
        if (json_data.RTM == 1) {
			document.querySelectorAll('.btn-rtm, .btn-rtm-spinner').forEach($elem => $elem.classList.toggle('d-none'));
			btn_actived = true;
		}
    });
});

function onClickActivate() {
	console.log(btn_actived);
    if (oh_class_global == 0) {
		
		document.getElementById('popuptText').innerHTML = 'Seat is EMPTY\n can\'t start ASANA';
		$('.hover_bkgr_fricc').show();
	}
	else {	
		document.getElementById('popuptText').innerHTML = 'Choose the profile';
		document.getElementById('btn-p1').classList.remove('d-none');
		document.getElementById('btn-p2').classList.remove('d-none');
		document.getElementById('btn-p3').classList.remove('d-none');
		document.getElementById('btn-p4').classList.remove('d-none');
		$('.hover_bkgr_fricc').show();	
	}
}


function onProfile1() {
 
	$('.hover_bkgr_fricc').hide();
	document.getElementById('btn-p1').classList.add('d-none');
	document.getElementById('btn-p2').classList.add('d-none');
	document.getElementById('btn-p3').classList.add('d-none');
	document.getElementById('btn-p4').classList.add('d-none');
	socket.emit('Activate_RTM','P1');
	console.log('Activate_RTM');
	// window.location.href = '/monitoring';	
	
}

function onProfile2() {
 
	$('.hover_bkgr_fricc').hide();
	document.getElementById('btn-p1').classList.add('d-none');
	document.getElementById('btn-p2').classList.add('d-none');
	document.getElementById('btn-p3').classList.add('d-none');
	document.getElementById('btn-p4').classList.add('d-none');
	socket.emit('Activate_RTM','P2');
	console.log('Activate_RTM');
	// window.location.href = '/monitoring';	
	
}


function onProfile3() {
 
	$('.hover_bkgr_fricc').hide();
	document.getElementById('btn-p1').classList.add('d-none');
	document.getElementById('btn-p2').classList.add('d-none');
	document.getElementById('btn-p3').classList.add('d-none');
	document.getElementById('btn-p4').classList.add('d-none');
	socket.emit('Activate_RTM','P3');
	console.log('Activate_RTM');
	// window.location.href = '/monitoring';	
	
}


function onProfile4() {
 
	$('.hover_bkgr_fricc').hide();
	document.getElementById('btn-p1').classList.add('d-none');
	document.getElementById('btn-p2').classList.add('d-none');
	document.getElementById('btn-p3').classList.add('d-none');
	document.getElementById('btn-p4').classList.add('d-none');
	socket.emit('Activate_RTM','P4');
	console.log('Activate_RTM');
	// window.location.href = '/monitoring';	
	
}



function onMonitoring() {
	
	console.log(btn_actived);
	if (oh_class_global == 0) {
		
		document.getElementById('popuptText').innerHTML = 'Seat is EMPTY\n can\'t start ASANA';
		$('.hover_bkgr_fricc').show();
	}
	else {
	window.location.href = '/monitoring';
	}
}
function onMonitoringConfort() {
	if (oh_class_global == 0) {
		document.querySelector('.hover_bkgr_fricc').style.display = 'block';
	}
	else {
	window.location.href = '/monitoring_confort';
	}
}

function onHMI() {
	
	console.log(btn_actived);
	btn_actived =false;
	document.querySelector('div[ocs-cl]').classList.remove('d-none');
	//document.querySelectorAll('.btn-ocs').classList.add('d-none');	
	document.querySelector('div[data-system]').classList.remove('d-none');						
	//document.querySelector('div[data-monitoring]').classList.add('d-none');
	document.querySelector('.debug').classList.add('d-none');
	document.querySelector('div[data-oh-global-cl]').classList.remove('d-none');
	}


function onClose() {
        $('.hover_bkgr_fricc').hide();
}

// Emit a call for snapshoting with current datetime, block while snapshoting is true
function onOCS() {
	
	window.location.href = '/seat_status';
}

function onClickSnapshot() {
    if(snapshoting) return;
    snapshoting = true;
    document.querySelectorAll('.btn-snapshot, .btn-snapshot-spinner').forEach(elem => elem.classList.toggle('d-none'));
    socket.emit('snapshot', moment(new Date()).local().toISOString());
	console.log('Start Snapshot');
}


function onClickNoProduction () {    
	document.querySelector('div[production-value]').classList.add('d-none');	
    document.querySelectorAll('.btn-reference, .btn-reference-spinner').forEach(elem => elem.classList.toggle('d-none'));
	referenceupdate = false;
}

function onClickYesProduction () {    
	document.querySelector('div[production-value]').classList.add('d-none');	
    socket.emit('Update_Refrence');
	console.log('Update Refrence');
}


function onUpdateReference() {
    if(referenceupdate) return;
    referenceupdate = true;
    document.querySelectorAll('.btn-reference, .btn-reference-spinner').forEach(elem => elem.classList.toggle('d-none'));
	document.querySelector('div[production-value]').classList.remove('d-none');	
	console.log('update production value');
}




// Emit a call for snapshoting with current datetime, block while snapshoting is true


function onClickUpdate() {
    if(timeupdate) return;
    timeupdate = true;
    document.querySelectorAll('.btn-update, .btn-update-spinner').forEach(elem => elem.classList.toggle('d-none'));
    socket.emit('timeupdate', moment(new Date()).local().toISOString());
}

// Set emptyValues & recalc poids values
function patchEmptyValues(values) {
    emptyValues = [...values];
    poids = OFFSETPOIDS.map((offset, index) => emptyValues[index] - offset);
}

function calculatePoids() {
    poids = OFFSETPOIDS.map((offset, index) => emptyValues[index] - offset);
}


function onClickHumanClass () {
	document.querySelector('li[human-cl-data]').classList.toggle('d-none');
}

// Linear fonction
function lerp(start, end, t) {
    return ((1 - t) * start) + (t * end);
}

// For main color calc avg between 3 colors
function calcLerp(ratio) {
    const rMin = 55, gMin = 255, bMin = 255;
    const rMed = 255, gMed = 178, bMed = 102; // light orange
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

// Calc rgb for a max color
function calcLerpWithMax(ratio, rMax, gMax, bMax) {
    const rMin = 55, gMin = 255, bMin = 255;
    const r = lerp(rMin, rMax, ratio * 1.75);
    const g = lerp(gMin, gMax, ratio * 1.75);
    const b = lerp(bMin, bMax, ratio * 1.75);
    return `rgb(${r}, ${g}, ${b})`;
}

// Calc ratio with 3 numbers
function calcRatio(start, end, nb) {
    if (nb > start) return 0;
    else if (nb < end) return 1;
    return (start - nb) / (start - end);
}

// Adapt data provided by server
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

function formatCsvStr(values) {
    return values.split(';').filter(str => !!str).map(str => +str.trim())
}
