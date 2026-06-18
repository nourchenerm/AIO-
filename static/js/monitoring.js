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
//const OFFSETPOIDS = [85000, 160000, 100000, 150000, 75000, 85000, 80000, 80000, 90000, 130000];
const OFFSETPOIDS_REF = [50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000];
OFFSETPOIDS = [50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000, 50000];

let rtm_actived = 0;

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
        //console.log(json_data);
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

        const [$pssc, psscValue] = [document.querySelector('li[data-pssc]'), json_data.init];
        // const [$searchPos, searchPosValue] = [document.querySelector('li[data-search-pos]'), json_data.state];
        const typePosValue = parseInt(json_data.final_position);
        const [$seat_condition, seat_condition] = [document.querySelector('li[data-seat-condition]'), json_data.dry_flag];
        const [$ohPos, oh_class] = [document.querySelector('li[data-oh-cl]'), json_data.object_human];
        const [$safety, safety_status] = [document.querySelector('li[data-safety]'), json_data.safe_unsafe];
        //const [$humanPos, human_class] = [document.querySelector('li[human-cl-data]'), json_data.human_class];
        const [$thorax, thorax_class] = [document.querySelector('li[data-thorax]'), Number(json_data.thorax_class)];
        const [$pelvis, pelvis_class] = [document.querySelector('li[data-pelvis]'), Number(json_data.pelvis_class)];
        const [$ex_thorax, ex_thorax_class] = [document.querySelector('li[data-extended-thorax]'), Number(json_data.thorax_ext_class)];
        const [$fidgetings, fidgetings_class] = [document.querySelector('li[data-fidgeting]'), Number(json_data.fidgeting_class)];
        const [$dissymetry, dissymetry_class] = [document.querySelector('li[data-dissymetry]'), Number(json_data.Dissymetry_class)];
        const [$leaning_forward, leaning_forward_class] = [document.querySelector('li[data-leaning_forward]'), Number(json_data.Leaning_forward_class)];
        const [$feet_on_dashboard, feet_on_dashboard_class] = [document.querySelector('li[data-feet_on_dashboard]'), Number(json_data.Feet_on_dashboard_class)];
        const $bmi_ls = document.querySelector('li[bmi-cl]')
        const $production = document.querySelector('div[production-value]')



        const $humanPos = document.querySelector('li[human-cl-data]')
        const [$human_class_button, human_class] = [document.querySelector('button[data-human-cl]'), json_data.human_class];

        const $rtm_active = document.querySelector('button[active-cl]')
        const $rtm_is_activated = document.querySelector('button[activated-cl]')
        rtm_actived = json_data.rtm_status;


        const $height = document.querySelector(`[bmid="0"]`);
        const $weight = document.querySelector(`[bmid="1"]`);
        const $bmi = document.querySelector(`[bmid="2"]`);


        // if (searchPosValue === 1) {
        //     firstStability = 1;
        // }

        document.querySelector('div[data-confort-score]').querySelector('span').innerHTML = json_data.confort_score;
        document.querySelector('div[data-confort-score-time]').querySelector('span').innerHTML = json_data.confort_score_time;
        document.querySelector('div[data-confort-score-fidgetings]').querySelector('span').innerHTML = json_data.confort_score_fidgeting;
        document.querySelector('div[data-confort-score-pelvis]').querySelector('span').innerHTML = json_data.confort_score_pelvis;
        document.querySelector('div[data-confort-score-thorax]').querySelector('span').innerHTML = json_data.confort_score_thorax;

        if (rtm_actived == true) {
            //$bmi_ls.classList.remove('d-none');
            $pssc.classList.remove('d-none');
            // document.querySelector('li[data-search-pos]').classList.remove('d-none');
            //$human_class_button.classList.remove('d-none');
            document.querySelectorAll('.btn-rtm, .btn-rtm-spinner').forEach($elem => $elem.classList.toggle('d-none'));
            btn_actived = true;
        } else {
            //$bmi_ls.classList.add('d-none');
            $pssc.classList.add('d-none');
            $human_class_button.classList.add('d-none');
            $humanPos.classList.add('d-none');

            // document.querySelector('li[data-search-pos]').classList.add('d-none');
        }

        if (safety_status == false) {
            
            $safety.querySelector('span').innerHTML = "Safe";
        }
        else
        {
            
            $safety.querySelector('span').innerHTML = "Unsafe";
        }

        if (seat_condition === 1) {
            $seat_condition.querySelector('span').innerHTML = "DRY";
        } else if (seat_condition === 2) {
            $seat_condition.querySelector('span').innerHTML = 'PRE_WET';
        } else if (seat_condition === 3) {
            $seat_condition.querySelector('span').innerHTML = 'WET';
        }

        // Uniquement si c'est stable
        // if (searchPosValue === 1) {
        //     if (psscValue === 1) {
        //         $pssc.innerHTML = "<span>Position PSSC found &#x2705;</span>";
        //         // $searchPos.querySelector('.loader').classList.add('d-none');

        //     }
        // } else {
            if (psscValue === 1) {
                $pssc.innerHTML = "<span>Position PSSC found &#x2705;</span>";
                // $searchPos.querySelector('span').innerHTML = "Unstable data...";
                // $searchPos.querySelector('.loader').classList.remove('d-none');
                if (json_data.fidgetings_alarm == 1) {
                    $fidgetings.classList.add('list-group-item-danger');
                } else {
                    if ($fidgetings.classList.contains('list-group-item-danger')) {
                        $fidgetings.classList.remove('list-group-item-danger');
                    }
                }
                switch (fidgetings_class) {
                    case 0:
                        $fidgetings.querySelector('span').innerHTML = "No Fidgeting";
                        break;
                    case 1:
                        $fidgetings.querySelector('span').innerHTML = "Fidgeting";
                        break;
                    default:
                        $fidgetings.querySelector('span').innerHTML = "(not available)";
                        break;
                }
            }


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
            $human_class_button.classList.add('d-none');
            $thorax.classList.add('d-none');
            $pelvis.classList.add('d-none');
            $ex_thorax.classList.add('d-none');
            $fidgetings.classList.add('d-none');
            $dissymetry.classList.add('d-none');
            $leaning_forward.classList.add('d-none');
            $feet_on_dashboard.classList.add('d-none');
            $bmi_ls.classList.add('d-none');
            $humanPos.classList.add('d-none');
            $rtm_active.classList.remove('d-none');
            $rtm_is_activated.classList.add('d-none');

        } else if (oh_class === 1) {
            $ohPos.querySelector('span').innerHTML = 'Object &#x2705;';
            $rtm_active.classList.remove('d-none');
            $rtm_is_activated.classList.add('d-none');
        } else if (oh_class === 2) {
            $ohPos.querySelector('span').innerHTML = 'Human &#x2705;';
            $rtm_active.classList.remove('d-none');
            $rtm_is_activated.classList.add('d-none');

            switch (human_class) {
                case 0:
                    $human_class_button.querySelector('span').innerHTML = "Baby";
                    break;
                case 1:
                    $human_class_button.querySelector('span').innerHTML = "Child";
                    break;
                case 2:
                    $human_class_button.querySelector('span').innerHTML = "5th perc";
                    break;
                case 3:
                    $human_class_button.querySelector('span').innerHTML = "50th perc";
                    break;
                case 4:
                    $human_class_button.querySelector('span').innerHTML = "95th perc";
                    break;
                case 5:
                    $human_class_button.querySelector('span').innerHTML = "Unknown";
                    break;
                default:
                    $human_class_button.querySelector('span').innerHTML = "(not available)";
                    break;
            }
            if (rtm_actived == true || btn_actived == true) {
                $thorax.classList.remove('d-none');
                $pelvis.classList.remove('d-none');
                $ex_thorax.classList.remove('d-none');
                $fidgetings.classList.remove('d-none');
                $dissymetry.classList.remove('d-none');
                $leaning_forward.classList.remove('d-none');
                $feet_on_dashboard.classList.remove('d-none');
                $rtm_active.classList.add('d-none');
                $rtm_is_activated.classList.remove('d-none');
                document.querySelector('div[data-monitoring]').classList.remove('d-none');
            } else {
                $thorax.classList.add('d-none');
                $pelvis.classList.add('d-none');
                $ex_thorax.classList.add('d-none');
                $fidgetings.classList.add('d-none');
                $dissymetry.classList.add('d-none');
                $leaning_forward.classList.add('d-none');
                $feet_on_dashboard.classList.add('d-none');
                $rtm_active.classList.remove('d-none');
                $rtm_is_activated.classList.add('d-none');
                document.querySelector('div[data-monitoring]').classList.add('d-none');
            }
            // if (searchPosValue === 1) {
            //     switch (typePosValue) {
            //         case 0:
            //             $searchPos.querySelector('span').innerHTML = 'Correct position &#x2705;';
            //             $searchPos.querySelector('.loader').classList.add('d-none');
            //             break;
            //         case 1:
            //             $searchPos.querySelector('span').innerHTML = 'Drifted position &#x274C;';
            //             break;
            //         case 2:
            //             $searchPos.querySelector('span').innerHTML = 'Drifted position &#x274C;';
            //             break;
            //         case 3:
            //             $searchPos.querySelector('span').innerHTML = 'Drifted position &#x274C;';
            //             break;
            //         case 6:
            //             $searchPos.querySelector('span').innerHTML = 'Drifted position &#x274C;';
            //             break;
            //         case 7:
            //             $searchPos.querySelector('span').innerHTML = 'Drifted position &#x274C;';
            //             break;
            //         case 8:
            //             $searchPos.querySelector('span').innerHTML = 'Drifted position &#x274C;';
            //             break;
            //         case 9:
            //             $searchPos.querySelector('span').innerHTML = 'Drifted position &#x274C;';
            //             break;
            //         case 10:
            //             $searchPos.querySelector('span').innerHTML = 'UNKNOWN position &#x274C;';
            //             $searchPos.querySelector('.loader').classList.add('d-none');
            //             break;
            //     }
           // }
            switch (thorax_class) {
                case 0:
                    $thorax.querySelector('span').innerHTML = "No thorax";
                    break;
                case 1:
                    $thorax.querySelector('span').innerHTML = "Thorax";
                    break;
                case 2:
                case 3:
                    $thorax.querySelector('span').innerHTML = "Unknown";
                    break;
                default:
                    $thorax.querySelector('span').innerHTML = "(not available)";
                    break;
            }

            switch (pelvis_class) {
                case 0:
                    $pelvis.querySelector('span').innerHTML = "No pelvis";
                    break;
                case 1:
                case 2:
                case 3:
                    $pelvis.querySelector('span').innerHTML = "Pelvis";
                    break;
                case 4:
                    $pelvis.querySelector('span').innerHTML = "Unknown";
                    break;
                default:
                    $pelvis.querySelector('span').innerHTML = "(not available)";
                    break;
            }

            switch (ex_thorax_class) {
                case 0:
                    $ex_thorax.querySelector('span').innerHTML = "No EX_thorax";
                    break;
                case 1:
                    $ex_thorax.querySelector('span').innerHTML = "Extended_thorax";
                    break;
                case 2:
                case 3:
                    $ex_thorax.querySelector('span').innerHTML = "Unknown";
                    break;
                default:
                    $ex_thorax.querySelector('span').innerHTML = "(not available)";
                    break;
            }
            switch (fidgetings_class) {
                case 0:
                    $fidgetings.querySelector('span').innerHTML = "No Fidgeting";
                    break;
                case 1:
                    $fidgetings.querySelector('span').innerHTML = "Fidgeting";
                    break;
                default:
                    $fidgetings.querySelector('span').innerHTML = "(not available)";
                    break;
            }
            switch (dissymetry_class) {
                case 0:
                    $dissymetry.querySelector('span').innerHTML = "No Dissymetry";
                    break;
                case 1:
                    $dissymetry.querySelector('span').innerHTML = "Dissymetry";
                    break;
                default:
                    $dissymetry.querySelector('span').innerHTML = "(not available)";
                    break;
            }
            switch (leaning_forward_class) {
                case 0:
                    $leaning_forward.querySelector('span').innerHTML = "No Leaning_forward";
                    break;
                case 1:
                    $leaning_forward.querySelector('span').innerHTML = "Leaning_forward";
                    break;
                default:
                    $leaning_forward.querySelector('span').innerHTML = "(not available)";
                    break;
            }
            switch (feet_on_dashboard_class) {
                case 0:
                    $feet_on_dashboard.querySelector('span').innerHTML = "No Feet on dashboard";
                    break;
                case 1:
                    $feet_on_dashboard.querySelector('span').innerHTML = "Feet on dashboard";
                    break;
                default:
                    $feet_on_dashboard.querySelector('span').innerHTML = "(not available)";
                    break;
            }


            if (json_data.dissymetry_alarm == 1) {
                $dissymetry.classList.add('list-group-item-danger');
            } else {
                if ($dissymetry.classList.contains('list-group-item-danger')) {
                    $dissymetry.classList.remove('list-group-item-danger');
                }
            }

            if (json_data.leaning_forward_alarm == 1) {
                $leaning_forward.classList.add('list-group-item-danger');
            } else {
                if ($leaning_forward.classList.contains('list-group-item-danger')) {
                    $leaning_forward.classList.remove('list-group-item-danger');
                }
            }

            if (json_data.feet_on_dashboard_alarm == 1) {
                $feet_on_dashboard.classList.add('list-group-item-danger');
            } else {
                if ($feet_on_dashboard.classList.contains('list-group-item-danger')) {
                    $feet_on_dashboard.classList.remove('list-group-item-danger');
                }
            }

            if (json_data.thorax_alarm == 1) {
                $thorax.classList.add('list-group-item-danger');
            } else {
                if ($thorax.classList.contains('list-group-item-danger')) {
                    $thorax.classList.remove('list-group-item-danger');
                }
            }

            if (json_data.pelvis_alarm == 1) {
                $pelvis.classList.add('list-group-item-danger');
            } else {
                if ($pelvis.classList.contains('list-group-item-danger')) {
                    $pelvis.classList.remove('list-group-item-danger');
                }
            }

            if (json_data.thorax_ext_alarm == 1) {
                $ex_thorax.classList.add('list-group-item-danger');
            } else {
                if ($ex_thorax.classList.contains('list-group-item-danger')) {
                    $ex_thorax.classList.remove('list-group-item-danger');
                }
            }

            if (json_data.fidgetings_alarm == 1) {
                $fidgetings.classList.add('list-group-item-danger');
            } else {
                if ($fidgetings.classList.contains('list-group-item-danger')) {
                    $fidgetings.classList.remove('list-group-item-danger');
                }
            }

            // json_data.human_list.forEach((element, i) => {
            //     const $cell = document.querySelector(`[classic="${i}"]`);
            //     $cell.querySelector('span').innerHTML = Math.round((element[1] * 100) / 1.2);
            // });

            $height.querySelector('span').innerHTML = json_data.height
            $weight.querySelector('span').innerHTML = json_data.weight
            $bmi.querySelector('span').innerHTML = json_data.bmi

        }

        if (oh_class != 2 && firstStability == 1) {

            firstStability = 0;
            // $searchPos.querySelector('span').innerHTML = 'Waiting for a person ';
            // $searchPos.querySelector('.loader').classList.remove('d-none');
            $thorax.classList.add('d-none');
            $pelvis.classList.add('d-none');
            $ex_thorax.classList.add('d-none');
            $fidgetings.classList.add('d-none');
            $bmi_ls.classList.add('d-none');
            $humanPos.classList.add('d-none');
            document.querySelector('div[data-monitoring]').classList.add('d-none');

            $pssc.classList.add('d-none');
            btn_actived = false;

        }

        if (debug_data == true) {
            debug_counter += 1;

            if (debug_counter % 4 == 0) {
                debug_counter = 0;
                json_data.avg.forEach((element, i) => {
                    // Apply color of looping captor : change coeff to move behavior of radius
                    const indexCapteur = (i + 1);
                    const $cell = document.querySelector(`td[data-value="c${indexCapteur}"]`);
                    $cell.querySelector('span').innerHTML = element;
                });
                json_data.occupied_offset.forEach((element, i) => {
                    // Apply color of looping captor : change coeff to move behavior of radius
                    const indexCapteur = (i + 1);
                    const $cell = document.querySelector(`td[offset-value="c${indexCapteur}"]`);
                    $cell.querySelector('span').innerHTML = element;
                });
            }
        }
    });

    // Event fire when countermeasure is emit by server (connection & change file)
    // 
    socket.on('massage_show', msg => {
        document.getElementById('popuptText').innerHTML = msg
        $('.hover_bkgr_fricc').show();
    });
    socket.on('massage_hide', msg => {
        $('.hover_bkgr_fricc').hide();
    });
    // if (debug_data == false) {
    // document.querySelector('.debug').classList.add('d-none');
    // console.log("Debug is hidden")
    // }
    // else {
    // console.log("Debug is visible")
    // }

    // Add eventlistener on snapshot btn
    document.querySelector('.btn-rtm').addEventListener('click', onClickActivate);
    document.querySelector('.btn-human-cl').addEventListener('click', onClickHumanClass);
    document.querySelector('.btn-pause').addEventListener('click', onPause);
    document.querySelector('.btn-resume').addEventListener('click', onResume);
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
        if (json_data.countermeasure_1 == 1) {
            counter_1 = true;
        } else {
            counter_1 = false;
        }
        if (json_data.countermeasure_2 == 1) {
            counter_2 = true;
        } else {
            counter_2 = false;
            clicked = false;
        }
        if (json_data.fidgeting == 1) {
            counter_3 = true;
        } else {
            counter_3 = false;
        }
    });
});


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


function onClickSnapshot() {
    if (snapshoting) return;
    snapshoting = true;
    document.querySelectorAll('.btn-snapshot, .btn-snapshot-spinner').forEach(elem => elem.classList.toggle('d-none'));
    socket.emit('snapshot', moment(new Date()).local().toISOString());
    console.log('Start Snapshot');
}


function onClickNoProduction() {
    document.querySelector('div[production-value]').classList.add('d-none');
    document.querySelectorAll('.btn-reference, .btn-reference-spinner').forEach(elem => elem.classList.toggle('d-none'));
    referenceupdate = false;
}

function onClickYesProduction() {
    document.querySelector('div[production-value]').classList.add('d-none');
    socket.emit('Update_Refrence');
    console.log('Update Refrence');
}

function onClickActivate() {
    console.log(btn_actived);
    if (oh_class_global == 0) {

        document.getElementById('popuptText').innerHTML = 'Seat is EMPTY\n can\'t start ASANA';
        $('.hover_bkgr_fricc').show();
    } else {
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
    socket.emit('Activate_RTM', 'P1');
    console.log('Activate_RTM');

}

function onProfile2() {

    $('.hover_bkgr_fricc').hide();
    document.getElementById('btn-p1').classList.add('d-none');
    document.getElementById('btn-p2').classList.add('d-none');
    document.getElementById('btn-p3').classList.add('d-none');
    document.getElementById('btn-p4').classList.add('d-none');
    socket.emit('Activate_RTM', 'P2');
    console.log('Activate_RTM');

}


function onProfile3() {

    $('.hover_bkgr_fricc').hide();
    document.getElementById('btn-p1').classList.add('d-none');
    document.getElementById('btn-p2').classList.add('d-none');
    document.getElementById('btn-p3').classList.add('d-none');
    document.getElementById('btn-p4').classList.add('d-none');
    socket.emit('Activate_RTM', 'P3');
    console.log('Activate_RTM');

}


function onProfile4() {

    $('.hover_bkgr_fricc').hide();
    document.getElementById('btn-p1').classList.add('d-none');
    document.getElementById('btn-p2').classList.add('d-none');
    document.getElementById('btn-p3').classList.add('d-none');
    document.getElementById('btn-p4').classList.add('d-none');
    socket.emit('Activate_RTM', 'P4');
    console.log('Activate_RTM');

}


function onPause() {
    if (rtm_actived == true && oh_class_global != 0) {
        document.querySelectorAll('.btn-pause, .btn-resume').forEach(elem => elem.classList.toggle('d-none'));
        socket.emit('Pause');
    } else {
        document.getElementById('popuptText').innerHTML = 'Activate ASANA Coach !!';
        $('.hover_bkgr_fricc').show();
    }
}

function onResume() {
    document.querySelectorAll('.btn-pause, .btn-resume').forEach(elem => elem.classList.toggle('d-none'));
    socket.emit('Resume');
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