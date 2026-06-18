const statusIndicator = document.querySelector('.status')
const statusMessage = document.querySelector('.status-message')
const button  = document.getElementById('button-test')
socket_=io();
console.log(statusIndicator)
console.log(statusMessage)
console.log(button)
var flag = false 
var oh_class_global = 0;
//flag = ! flag	
document.querySelector('.nav-monitoring').addEventListener('click', onMonitoring);
document.querySelector('.popupCloseButton').addEventListener('click', onClose);
//document.querySelector('.nav-monitoring-confort').addEventListener('click', onMonitoringConfort);
//button.onclick = () =>
socket_.on('values', result => {
    
  
    console.log(data);

    if(data.ods == 1){
        document.getElementById("seatStatus").innerHTML =
            "Seat is Occupied";
    }
    else{
        document.getElementById("seatStatus").innerHTML =
            "Seat is Empty";
    }

});



function onMonitoring() {
	// console.log(oh_class_global)
	// if (oh_class_global == 0 || oh_class_global == 99 ) {
	// 	document.querySelector('.hover_bkgr_fricc').style.display = 'block';
	// }
	// else {
	window.location.href = '/monitoring';
	//}
}
function onMonitoringConfort() {
	// if (oh_class_global == 0) {
	// 	document.querySelector('.hover_bkgr_fricc').style.display = 'block';
	// }
	// else {
	window.location.href = '/monitoring_confort';
	//}
}
function onClose() {
        $('.hover_bkgr_fricc').hide();
}