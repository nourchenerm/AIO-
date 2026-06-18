//const host = 'http://192.168.1.8:5000/'
// GLOBAL VAR
const socket = io();
let snapshoting = false;
let referenceupdate = false;
let debug_counter = 0;
let btn_actived = false;
let debug_data = true
var ip = location.host;
var bad_posture_global = 0;

let last_human_class = 0;
// metrics values
let emptyValues = [];
let poids = [];
//const OFFSETPOIDS = [85000, 160000, 100000, 150000, 75000, 85000, 80000, 80000, 90000, 130000];
const OFFSETPOIDS_REF = [50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000];
OFFSETPOIDS = [50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000];

let rtm_actived = 0;
const sensors = [0,1,3,4,5,6,8,9];

// On DOM Loaded
window.addEventListener("DOMContentLoaded", (event) => {

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
            
            $stops.forEach(function($stop, index2) {
                $stop.setAttribute('stop-color', colors[index2]);
                const radius = ratio / 2.5;
                $stop.closest('radialGradient').setAttribute('r', radius > 0.6 ? 0.6 : (radius > 0.2 ? radius : 0.2));
            });
        });
        const [$posture, bad_posture] = [document.querySelector('li[data-posture]'), json_data.bad_posture];
        const  $ohPosGlobal= document.querySelector('div[data-oh-global-cl]');
        const oh_class = json_data.object_human;

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

        rtm_actived = json_data.rtm_status;
        console.log(json_data.start_unsafe);
        if (json_data.start_unsafe === 1 ) {
            
            document.getElementById('start').disabled = true ;

        }
        else 
        {
            
            document.getElementById('start').disabled = false ;
        }

        bad_posture_global = bad_posture;
        if (bad_posture === -2) {
            $posture.querySelector('span').innerHTML = "UNKNOWN";
        } else if (bad_posture === -1) {
            $posture.querySelector('span').innerHTML = "UNSAFE";
        }else if (bad_posture === 0) {
            $posture.querySelector('span').innerHTML = "GOOD_POSTURE";
        } else if (bad_posture === 1) {
            $posture.querySelector('span').innerHTML = "DISSYMMETRY_RIGHT";
        } else if (bad_posture === 2) {
            $posture.querySelector('span').innerHTML = "DISSYMMETRY_LEFT";
        } else if (bad_posture === 3) {
            $posture.querySelector('span').innerHTML = "BACK_NO_CONTACT";
        } else if (bad_posture === 4) {
            $posture.querySelector('span').innerHTML = "PELVIS_DRIFT";
        } else if (bad_posture === 5) {
            $posture.querySelector('span').innerHTML = "SIDE_LYING_RIGHT";
        } else if (bad_posture === 6) {
            $posture.querySelector('span').innerHTML = "SIDE_LYING_LEFT";
        }


        if (json_data.driving_mode === 1)            
            document.getElementById('driving_mode').innerHTML = "Driving";
        else if (json_data.driving_mode === 2)
            document.getElementById('driving_mode').innerHTML = "Automated Drive";
        else if (json_data.driving_mode === 3)
            document.getElementById('driving_mode').innerHTML = "Relax Max";


        oh_class_global = oh_class;
		if (oh_class === 0 ) {
			$ohPosGlobal.innerHTML = "Empty Seat";	            
            document.getElementById('belt-on').classList.remove('d-none');
            document.getElementById('belt-off').classList.add('d-none');	            
            document.getElementById('belt-on').disabled = true;
            document.getElementById('driving_mode').disabled = true;
            document.getElementById('driving_mode').innerHTML = "DRIVING MODE";            
            document.getElementById('start').disabled = false ;

			
		} else if (oh_class === 1) {		
			$ohPosGlobal.innerHTML = 'Object &#x2705;';            
            document.getElementById('belt-on').classList.remove('d-none');
            document.getElementById('belt-off').classList.add('d-none');
            document.getElementById('belt-on').disabled = true;
            document.getElementById('driving_mode').disabled = true;
            
            document.getElementById('driving_mode').innerHTML = "DRIVING MODE";
		} else if (oh_class === 2) {
			$ohPosGlobal.innerHTML ='Human &#x2705;';
            document.getElementById('belt-on').disabled = false;
            document.getElementById('driving_mode').disabled = false;
        }

        if (debug_data == true) {
            debug_counter += 1;
            // console.log(json_data.good_position);
            // console.log(json_data.percentage_disymmetry);

            if (debug_counter % 4 == 0) {
                debug_counter = 0;
                i=0;
                json_data.good_position.forEach((element) => {
                    // Apply color of looping captor : change coeff to move behavior of radius
                    if (sensors.includes(i)){
                    //     i=i+1;
                    // 
                    const indexCapteur = (i + 1);
                    const $cell = document.querySelector(`td[data-value="c${indexCapteur}"]`);
                    $cell.querySelector('span').innerHTML = element;
                    
                }
                i=i+1;
                });
                i=0;
                json_data.percentage_disymmetry.forEach((element) => {                                     
                    // Apply color of looping captor : change coeff to move behavior of radius
                     if (sensors.includes(i)){
                    //     i=i+1;
                    // }
                    const indexCapteur = (i + 1);
                    const $cell = document.querySelector(`td[offset-value="c${indexCapteur}"]`);
                    $cell.querySelector('span').innerHTML = parseInt(element*100);
                    
                     }
                     i=i+1;
                });
            }
        }
    });

    // Add eventlistener on snapshot btn
    document.querySelector('.nav-monitoring').addEventListener('click', onMonitoring);
    //document.querySelector('.nav-monitoring-confort').addEventListener('click', onMonitoringConfort);
    document.querySelector('.nav-hmi').addEventListener('click', onHMI);
    document.querySelector('.popupCloseButton').addEventListener('click', onClose);
    document.getElementById('belt-on').addEventListener('click', onClickBeltON);
    document.getElementById('belt-off').addEventListener('click', onClickBeltOFF);
    document.getElementById('driving_mode').addEventListener('click', onClickDrivingMode);
    document.getElementById('btn-p1').addEventListener('click', onDriving);
    document.getElementById('btn-p2').addEventListener('click', onAutomatedDrive);
    document.getElementById('btn-p3').addEventListener('click', onRelaxMax);
    document.getElementById('start').addEventListener('click', onStart);
    

    // Event fire when snapshotDone is emit by server (file[1] === 0)
    socket.on('snapshotDone', (values) => {
        console.log('snapshot done');
        document.querySelectorAll('.btn-snapshot, .btn-snapshot-spinner').forEach($elem => $elem.classList.toggle('d-none'));
        snapshoting = false;
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
        if (json_data.belt_status === 1 ) {
            
            document.getElementById('belt-on').classList.add('d-none');
            document.getElementById('belt-off').classList.remove('d-none');

        }
        else 
        {
            
            document.getElementById('belt-on').classList.remove('d-none');
            document.getElementById('belt-off').classList.add('d-none');
        }

    });
});

function onStart() {
    socket.emit('START_UNSAFE');
    document.getElementById('start').disabled = true ;
}

function onHMI() {
    debug_data = false;
    document.querySelector('div[data-system]').classList.remove('d-none');
}

function onMonitoring() {
    debug_data = true;
    document.querySelector('div[data-system]').classList.add('d-none');
    window.location.href = '/monitoring';
}

function onMonitoringConfort() {
    debug_data = false;
    // document.querySelector('div[data-system]').classList.add('d-none');	
    window.location.href = '/monitoring_confort';
}


function onClose() {
    $('.hover_bkgr_fricc').hide();
}


function onClickBeltON() {

    socket.emit('BELT', 1);
    document.getElementById('belt-on').classList.add('d-none');
    document.getElementById('belt-off').classList.remove('d-none');

}

function onClickBeltOFF() {

    socket.emit('BELT', 0);
    document.getElementById('belt-on').classList.remove('d-none');
    document.getElementById('belt-off').classList.add('d-none');
}

function onClickDrivingMode() {

    // document.getElementById('popuptText').innerHTML = 'Choose the Driving Mode';
    document.getElementById('btn-p1').classList.remove('d-none');
    document.getElementById('btn-p2').classList.remove('d-none');
    document.getElementById('btn-p3').classList.remove('d-none');
    $('.hover_bkgr_fricc').show();
}

function onDriving() {

    $('.hover_bkgr_fricc').hide();
    document.getElementById('btn-p1').classList.add('d-none');
    document.getElementById('btn-p2').classList.add('d-none');
    document.getElementById('btn-p3').classList.add('d-none');
    socket.emit('Driving_Mode', '1');
    document.getElementById('driving_mode').innerHTML = "Driving";
    console.log('Driving_Mode Driving');

}

function onAutomatedDrive() {

    $('.hover_bkgr_fricc').hide();
    document.getElementById('btn-p1').classList.add('d-none');
    document.getElementById('btn-p2').classList.add('d-none');
    document.getElementById('btn-p3').classList.add('d-none');
    socket.emit('Driving_Mode', '2');
    document.getElementById('driving_mode').innerHTML = "Automated Drive";
    console.log('Driving_Mode Automated Drive');

}


function onRelaxMax() {

    $('.hover_bkgr_fricc').hide();
    document.getElementById('btn-p1').classList.add('d-none');
    document.getElementById('btn-p2').classList.add('d-none');
    document.getElementById('btn-p3').classList.add('d-none');
    socket.emit('Driving_Mode', '3');
    document.getElementById('driving_mode').innerHTML ="Relax Max";
    console.log('Driving_Mode Relax Max');

}

// Set emptyValues & recalc poids values
function patchEmptyValues(values) {
    emptyValues = [...values];
    poids = OFFSETPOIDS.map((offset, index) => emptyValues[index] - offset);
}


function calculatePoids() {
    poids = OFFSETPOIDS.map((offset, index) => emptyValues[index] - offset);
}

function onClickHumanClass() {
    document.querySelector('li[human-cl-data]').classList.toggle('d-none');
}

// Linear fonction
function lerp(start, end, t) {
    return ((1 - t) * start) + (t * end);
}

// For main color calc avg between 3 colors
function calcLerp(ratio) {
    const rMin = 55,
        gMin = 255,
        bMin = 255;
    const rMed = 255,
        gMed = 178,
        bMed = 102; // light orange
    const rMax = 255,
        gMax = 0,
        bMax = 0;

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
    const rMin = 55,
        gMin = 255,
        bMin = 255;
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
        else throw ('type is not good');


        return result;
    } catch (error) {
        console.error('ERROR FOR TYPE you have to choose between simulation, data or log', type)
    }
}

function formatCsvStr(values) {
    return values.split(';').filter(str => !!str).map(str => +str.trim())
}