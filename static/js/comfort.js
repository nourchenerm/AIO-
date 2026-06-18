// GLOBAL VAR
const socket = io();
let snapshoting = false;
let chartBack;
let chartCushion;
let isTimeRefSetted = false;
let timeRef;
let duration = 2;
let valuesReceived = 11;
let acquisitions = 10;
let isPaused = false;
var oh_class_global = 0;
let rtm_actived = 0;

var exercice = "";
const exercice_list = ["Respiration", "étirement_cambrer", "gainage", "étirement", "Start_Reprendre"];
var profil = "P1";

// metrics values
let emptyValues = [];
var timeLabel=-1;
// On DOM Loaded
window.addEventListener("DOMContentLoaded", (event) => {
	
	document.getElementById('pause').addEventListener('click', onPause);
	document.getElementById('resume').addEventListener('click', onResume);
	document.querySelector('.btn-rtm').addEventListener('click', onClickActivate);
	document.getElementById('btn-p1').addEventListener('click', onProfile1);
	document.getElementById('btn-p2').addEventListener('click', onProfile2);
	document.getElementById('btn-p3').addEventListener('click', onProfile3);
	document.getElementById('btn-p4').addEventListener('click', onProfile4);
	document.getElementById('id_Confort_Score').addEventListener('click', onScore);
	document.getElementById('id_Confort_Time').addEventListener('click', onTime);
	document.getElementById('id_Confort_Fixed').addEventListener('click', onFixed);
	document.getElementById('id_Confort_Thorax').addEventListener('click', onThorax);
	document.getElementById('id_Confort_Pelvis').addEventListener('click', onPelvis);
	document.getElementById('validate_time').addEventListener('click', emitRTM);	
	document.getElementById("Start_Reprendre").loop = false;
	document.getElementById("étirement").loop = false;
	document.getElementById("gainage").loop = false;
	document.getElementById("étirement_cambrer").loop = false;
	document.getElementById("Respiration").loop = false;
	
	document.getElementById('Start_Reprendre').addEventListener("ended", () => {
		  console.log('ended')
		});

    configControls();
    initCharts();
    // Event fire when empty values is emit by server (connection & change file)
    // cf : snapshot_empty_values.csv
    socket.on('emptyValues', newEmptyValues => {
        console.log('New empty values');
        patchEmptyValues(adpaterData('emptyValues', newEmptyValues));
    });

    // Event fire when values of captors is emit by server (connection & change file)
    // cf : OneLineData.csv
    socket.on('values', result => {

        if (!result || !emptyValues.length) return;

        const json_data = adpaterData('data', result);
        if (!isTimeRefSetted) {
            // timeRef = formatCsvStr(result).slice(0,1);
            timeRef = toTimestamp(json_data.time);
            isTimeRefSetted = true;
            console.log("Time reference setted = " + timeRef);
        }
		if (json_data.rtm_status == true){
			if (timeLabel != (toTimestamp(json_data.time) - timeRef))
			{	
		
				timeLabel = formatDuration(toTimestamp(json_data.time) - timeRef);
				updateChartsLabels(timeLabel);
				updateChartsValues(json_data.confort_score, 0);
				updateChartsValues(json_data.confort_score_time, 1);
				updateChartsValues(json_data.confort_score_fidgeting, 2);
				updateChartsValues(json_data.confort_score_pelvis, 3);
				updateChartsValues(json_data.confort_score_thorax, 4);
				if (!isPaused) {
					chartBack.update();
				}	
				timeLabel = (toTimestamp(json_data.time) - timeRef);
			}
			
			var duration = moment.duration(json_data.execution_time*1000);
			 if (duration.asHours() > 1) {			 
				document.getElementById('time').innerHTML = (Math.floor(duration.asHours()) + moment(duration.asMilliseconds()).format("mm:ss:SSS")); 
			 }
			 else {			 
				document.getElementById('time').innerHTML = moment(duration.asMilliseconds()).format("00:mm:ss:SSS"); 
			 }
			 
			let res = Math.round(json_data.confort_score * 100/80 * 100) / 100	
			document.getElementById('pourcentage_cercle').style.strokeDasharray = json_data.confort_score
			document.getElementById('pourcentage_text').innerHTML = json_data.confort_score 
			
			document.getElementById('Fix_Bar').style.width = (json_data.Fix_Bar)+"%" ;
			document.getElementById('Bassin_Bar').style.width = (json_data.Bassin_Bar)+"%" ;
			document.getElementById('Dos_Bar').style.width = (json_data.Dos_Bar)+"%" ;
			
		}
		rtm_actived = json_data.rtm_status;
		oh_class_global =json_data.object_human ;
		if (rtm_actived == false && oh_class_global != 0)
		{
			document.getElementById("ASANA_Coach").disabled = false;
			document.getElementById("ASANA_Coach").style.opacity = "unset";	
			document.getElementById("ASANA_Coach").style.cursor = "pointer";
		}
		else {
			
			document.getElementById("ASANA_Coach").disabled = true;			
			document.getElementById("ASANA_Coach").style.opacity = ".50";	
			document.getElementById("ASANA_Coach").style.cursor = "unset";
		}
		
    });
	
	socket.on('countermeasure', msg => {
		hidePopUpButton ();
		const words = msg.split('/');
		document.getElementById('popuptText').innerHTML =words[0]
		for (let i = 1; i < words.length - 1; i++) {
				
			document.getElementById('btn-p'+i).style.display = "unset";
			document.getElementById('btn-p'+i).innerHTML = words[i]
		}
		
		
		if (exercice_list.includes (words[words.length-1]) == true ) {
			exercice = words[words.length-1];
			}
		document.getElementById('ClosButton').style.display = "none";
		$('.hover_bkgr_fricc').show();
    });
	
	socket.on('massage_show', msg => {
		hidePopUpButton ();
		const words = msg.split('/');
		document.getElementById('popuptText').innerHTML =words[0]
		for (let i = 1; i < words.length; i++) {
				
			document.getElementById('btn-p'+i).style.display = "unset";
			document.getElementById('btn-p'+i).innerHTML = words[i]
		}
		
		document.getElementById('ClosButton').style.display = "none";
		$('.hover_bkgr_fricc').show();
    });
	
	socket.on('countermeasure_hide', msg => {	
		$('.hover_bkgr_fricc').hide();
    });
});


function onScore() {
    chartBack.data.datasets[0].hidden = !chartBack.data.datasets[0].hidden;
    chartBack.update();

    var isHidden = chartBack.data.datasets[0].hidden;
	if (isHidden) {
        document.getElementById('id_Confort_Score').style.backgroundColor= "white";
    }
    else {
        document.getElementById('id_Confort_Score').style.backgroundColor= "rgb(255, 165, 2)";
    }

}

function onTime() {
    chartBack.data.datasets[1].hidden = !chartBack.data.datasets[1].hidden;
    chartBack.update();

    var isHidden = chartBack.data.datasets[1].hidden;
	if (isHidden) {
        document.getElementById('id_Confort_Time').style.backgroundColor= "white";
        document.getElementById('id_Confort_Time').style.color= "black";
    }
    else {
        document.getElementById('id_Confort_Time').style.backgroundColor= "rgb(55, 66, 250)";
        document.getElementById('id_Confort_Time').style.color= "white";
    }

}

function onFixed() {
    chartBack.data.datasets[2].hidden = !chartBack.data.datasets[2].hidden;
    chartBack.update();

    var isHidden = chartBack.data.datasets[2].hidden;
	if (isHidden) {
        document.getElementById('id_Confort_Fixed').style.backgroundColor= "white";
    }
    else {
        document.getElementById('id_Confort_Fixed').style.backgroundColor= "rgb(46, 213, 115)";
    }

}

function onThorax() {
    chartBack.data.datasets[4].hidden = !chartBack.data.datasets[4].hidden;
    chartBack.update();

    var isHidden = chartBack.data.datasets[4].hidden;
	if (isHidden) {
        document.getElementById('id_Confort_Thorax').style.backgroundColor= "white";
    }
    else {
        document.getElementById('id_Confort_Thorax').style.backgroundColor= "rgb(194, 54, 22)";
    }

}

function onPelvis() {
    chartBack.data.datasets[3].hidden = !chartBack.data.datasets[3].hidden;
    chartBack.update();

    var isHidden = chartBack.data.datasets[3].hidden;
	if (isHidden) {
        document.getElementById('id_Confort_Pelvis').style.backgroundColor= "white";
        document.getElementById('id_Confort_Pelvis').style.color= "black";
    }
    else {
        document.getElementById('id_Confort_Pelvis').style.backgroundColor= "black";
        document.getElementById('id_Confort_Pelvis').style.color= "white";
    }

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
        else throw('type is not good');


        return result;
    } catch (error) {
        console.error('ERROR FOR TYPE you have to choose between simulation, data or log', type)
    }
}

function toTimestamp(strDate){
    var datum = Date.parse(strDate);
    return datum/1000;
   }

function formatCsvStr(values) {
    return values.split(';').filter(str => !!str).map(str => +str.trim())
}

function initCharts() {

    var ctx = document.getElementById('backSensorsChart').getContext('2d');
    chartBack = new Chart(ctx, {
        // The type of chart we want to create
        type: 'line',

        // The data for our dataset
        data: {
            labels: [],
            datasets: [{
                label: 'Confort Score',
                borderColor: 'rgb(255, 165, 2)',
                order: 3,
                data: []
            },
            {
                label: 'Confort time',
                borderColor: 'rgb(55, 66, 250)',
                order: 1,
                data: []
            },
            {
                label: 'Confort fixed posture',
                borderColor: 'rgb(46, 213, 115)',
                order: 4,
                data: []
            },
            {
                label: 'Confort pelvis drift',
                borderColor: 'rgb(47, 53, 66)',
                order: 2,
                data: []
            },
            {
                label: 'Confort rounded back',
                borderColor: 'rgb(194, 54, 22)',
                order: 5,
                data: []
            }]
        },

        // Configuration options go here
        options: {
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
                        labelString: 'Time',
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
                        labelString: '',
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
                        suggestedMin: 79.7,
                        suggestedMax: 80.2
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
                        onZoom: function({chart}) {
                            document.querySelector('.btn-chart-resetZoom').style.display = "inline-block";
                        }
                    }
                }
            }
        }
    });
}


function onPause() {
	if (rtm_actived == true && oh_class_global != 0)
	{
		console.log("Charts Pause");
		isPaused = true;
		chartBack.stop();
		document.getElementById('pause').style.display = "none";
		document.getElementById('resume').style.display = "unset";	
		isPaused = true;
		socket.emit('Pause');
	}
	else if ( oh_class_global == 0) {
		document.getElementById('popuptText').innerHTML = 'Empty Seat !!';	
		document.getElementById('ClosButton').style.display = "unset";	
		hidePopUpButton ();
		$('.hover_bkgr_fricc').show();		
	}
	else if ( rtm_actived == false) {
		document.getElementById('popuptText').innerHTML = 'Activate ASANA Coach !!';	
		document.getElementById('ClosButton').style.display = "unset";	
		hidePopUpButton ();
		$('.hover_bkgr_fricc').show();		
	}
}

function onResume() {
	console.log("Charts Resume")
    isPaused = false;
    chartBack.render();
    document.getElementById('pause').style.display = "unset";
	document.getElementById('resume').style.display = "none";
    socket.emit('Resume');
}

function configControls() {
	document.querySelector('.nav-monitoring').addEventListener('click', onMonitoring);
	//document.querySelector('.nav-monitoring-confort').addEventListener('click', onMonitoringConfort);
	document.querySelector('.popupCloseButton').addEventListener('click', onClose);
}

function onClickChartPause() {
    console.log("Charts Pause");
    isPaused = true;
    chartBack.stop();
    document.querySelector('.btn-chart-pause').style.display = "none";
    document.querySelector('.btn-chart-resume').style.display = "inline-block";
}

function onClickChartResume() {
    console.log("Charts Resume")
    isPaused = false;
    chartBack.render();
    document.querySelector('.btn-chart-resume').style.display = "none";
    document.querySelector('.btn-chart-pause').style.display = "inline-block";
}

function onClickChartClear() {
    console.log("Chart Clear")

    chartBack.data.labels = [];

    chartBack.data.datasets.forEach((set , i) => {
        set.data = [];
    });


    chartBack.clear();
    onClickChartResume();
    chartBack.update();
}

function onClickResetZoom() {
    console.log("Reset Zoom");
    chartBack.resetZoom();
    document.querySelector('.btn-chart-resetZoom').style.display = "none";
}



function updateChartsValues(rawValue, sensorIndex) {

    //console.log("----------------- VALUES ----------------------")
    var value = rawValue - emptyValues[sensorIndex];
    var maxChartValues = duration * acquisitions;
    //console.log("Max = " + maxChartValues)



	var chartBackValuesLength = chartBack.data.datasets[sensorIndex].data.length;
	//console.log("Back[" + sensorIndex + "] = " + chartBackValuesLength)

	if (chartBackValuesLength < maxChartValues)
		chartBack.data.datasets[sensorIndex].data.push(rawValue);
	else {
		var overflow = chartBackValuesLength - maxChartValues
		//console.log("Back overflow = " + overflow);

		//console.log("Back before slice = " + chartBack.data.datasets[sensorIndex].data.length);
		var newValuesArray = chartBack.data.datasets[sensorIndex].data.slice(overflow + 1);
		//console.log("Back after slice = " + newValuesArray.length);

		chartBack.data.datasets[sensorIndex].data = newValuesArray;
		chartBack.data.datasets[sensorIndex].data.push(rawValue);
		//console.log("Back after push = " + chartBack.data.datasets[sensorIndex].data.length);
	}
	if (rawValue - chartBack.options.scales.yAxes[0].ticks.Min < 0,2)
	{
		chartBack.options.scales.yAxes[0].ticks.Max = chartBack.options.scales.yAxes[0].ticks.Max - 0,8 ;
	}

    //console.log("----------------- !VALUES ----------------------")
}

function updateChartsLabels(timeLabel) {

    //console.log("----------------- LABELS ----------------------")
    var chartBackLabelsLength = chartBack.data.labels.length;
    //console.log("Back = " + chartBackLabelsLength)

    var maxChartLabels = duration * acquisitions;
    //console.log("Max = " + maxChartLabels)

    if (chartBackLabelsLength < maxChartLabels)
        chartBack.data.labels.push(timeLabel);
    else {
        var overflow = chartBackLabelsLength - maxChartLabels;
        //console.log("Back overflow = " + overflow);
        //console.log("Before slice = " + chartBack.data.labels.length);
        var newLabelsArray = chartBack.data.labels.slice(overflow + 1);
        //console.log("After slice = " + newLabelsArray.length);

        chartBack.data.labels = newLabelsArray;
        chartBack.data.labels.push(timeLabel);
        //console.log("After push = " + chartBack.data.labels.length);
    }


    //console.log("----------------- !LABELS ----------------------")
}

function formatDuration(ms) {
    let duration = moment.duration(ms* 1000);
      return moment(duration.asMilliseconds()).format("mm:ss");

}
function onMonitoring() {
	if (oh_class_global == 0) {
		document.getElementById('popuptText').innerHTML = 'Empty Seat !!';	
		document.getElementById('ClosButton').style.display = "unset";	
		hidePopUpButton ();
		$('.hover_bkgr_fricc').show();
	}
	else {
	window.location.href = '/monitoring';
	}
}

function onMonitoringConfort() {
	if (oh_class_global == 0) {	
	
		document.getElementById('popuptText').innerHTML = 'Empty Seat !!';	
		document.getElementById('ClosButton').style.display = "unset";	
		hidePopUpButton ();
		$('.hover_bkgr_fricc').show();

	
		// hidePopUpButton ();		
		// document.getElementById('ClosButton').style.display = "unset";
		// document.querySelector('.hover_bkgr_fricc').style.display = 'block';
	}
	else {
	window.location.href = '/monitoring_confort';
	}
}
function onClose() {
        $('.hover_bkgr_fricc').hide();
}

function onClickActivate() {
    if (oh_class_global == 0) {
		
		document.getElementById('popuptText').innerHTML = 'Seat is EMPTY\n can\'t start ASANA';
		hidePopUpButton ();		
		document.getElementById('ClosButton').style.display = "unset";
		$('.hover_bkgr_fricc').show();
	}
	else {	
		document.getElementById('popuptText').innerHTML = 'Choose the profile';
		
		showPopUpButton ()		
		for (let i = 1; i < 5; i++) {
				
			document.getElementById('btn-p'+i).innerHTML = "Profile "+i
		}
		document.getElementById('ClosButton').style.display = "none";
		$('.hover_bkgr_fricc').show();	
		
		//show(document.getElementById('popup'));
	}
}


function emitRTM() {
	if (profil == "P1" ) {
		socket.emit('Activate_RTM','P1');
		console.log('Activate_RTM P1 ' + document.querySelector('input[type="time"]').value);
		$('.hover_bkgr_fricc_time').hide();	
	}
	else if (profil == "P2" ) {
		socket.emit('Activate_RTM','P2');
		console.log('Activate_RTM P2 '+ document.querySelector('input[type="time"]').value);
		$('.hover_bkgr_fricc_time').hide();	

	}
	else if (profil == "P3" ) {
		socket.emit('Activate_RTM','P3');
		console.log('Activate_RTM P3 '+ document.querySelector('input[type="time"]').value);
		$('.hover_bkgr_fricc_time').hide();	

	}
	else if (profil =="P4" ) {
		socket.emit('Activate_RTM','P4');
		console.log('Activate_RTM P4 '+ document.querySelector('input[type="time"]').value);
		$('.hover_bkgr_fricc_time').hide();	

	}	
}

function onProfile1() {
	if (rtm_actived == false ) {
		
		$('.hover_bkgr_fricc').hide();
		hidePopUpButton ();
		$('.hover_bkgr_fricc_time').show();	
		profil = "P1";		
	}	
	else {
		
		$('.hover_bkgr_fricc').hide();
		socket.emit('countermeasure_answer','False');
	}
	
}

function onProfile2() {
 
	
	if (rtm_actived == false) {
		$('.hover_bkgr_fricc').hide();
		hidePopUpButton ();
		$('.hover_bkgr_fricc_time').show();	
		profil = "P2";	
	}
	else {
		
		$('.hover_bkgr_fricc').hide();
		if (exercice_list.includes (exercice) == true ) {
			document.getElementById(exercice).play();
		}
		socket.emit('countermeasure_answer','True');
	}		
	
}


function onProfile3() {
	if (rtm_actived == false) {
		$('.hover_bkgr_fricc').hide();
		hidePopUpButton ();
		$('.hover_bkgr_fricc_time').show();	
		profil = "P3";	
	}
		
	
}


function onProfile4() {
 
	if (rtm_actived == false) {
		$('.hover_bkgr_fricc').hide();
		hidePopUpButton ();
		$('.hover_bkgr_fricc_time').show();	
		profil = "P4";	
	}
}

function hidePopUpButton () {
	
	document.getElementById('btn-p1').style.display = "none";
	document.getElementById('btn-p2').style.display = "none";
	document.getElementById('btn-p3').style.display = "none";
	document.getElementById('btn-p4').style.display = "none";

}


function showPopUpButton () {
	
	document.getElementById('btn-p1').style.display = "unset";
	document.getElementById('btn-p2').style.display = "unset";
	document.getElementById('btn-p3').style.display = "unset";
	document.getElementById('btn-p4').style.display = "unset";

}
