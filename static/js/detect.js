const resultStatus = document.getElementById("result-status");
const resultName = document.getElementById("result-name");
const resultType = document.getElementById("result-type");
const video = document.getElementById("video");
const scanCount = document.getElementById("scan-count");
const scannedInfo = document.getElementById("scanned-info");
var event_pk = document.getElementById("event_pk").value;
var endpoint = document.getElementById("endpoint").value;
var last_scanned_uid = null;

const qrCodeScanner = new Html5Qrcode("video");
function startScanning() {
    qrCodeScanner.start(
      { facingMode: "environment" },
      {
        fps: 10,
      },
      (decodedText, decodedResult) => {
          get_status(decodedText);
        // onSuccess callback, called when a QR code is successfully scanned
      },
      (errorMessage) => {
        // onError callback, called in case of errors

      }
    );
  }

function get_status(uid){
    if(last_scanned_uid == uid){
      console.log("just scanned this... No change")
      pause = false;
      return;
    }
    
    fetch(endpoint + "?uid=" + uid + "&event_pk=" + event_pk, {
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        updateData(data);
        last_scanned_uid = uid;
        pasue = false;
        // showQRresult();
    })
}

function updateData(data){
  console.log(data);
  if(data.status == "no-change"){
    return;
  }
  if(data.status == "error"){
    resultStatus.innerHTML = "Unusable QR";
    video.style.borderColor = "red";
  }
  else{
    if (data.status == 'valid'){
      resultStatus.innerHTML = "Valid";
      video.style.borderColor = "green";
      scannedInfo.insertAdjacentHTML("afterbegin", "<div>" + data.scan_info + "</div>");
      document.getElementById("not-scanned-" + data.pk).remove();
  }
  else if (data.status == 'scanned'){
    resultStatus.innerHTML = "Already Scanned";
    video.style.borderColor = "yellow";
  }
  else if (data.status == 'invalid'){
    resultStatus.innerHTML = "Invalid";
    video.style.borderColor = "red";
  }
  else{
    resultStatus.innerHTML = "QR Code not found";
  }
  resultName.innerHTML = data.name;
  resultType.innerHTML = data.tag;
  scanCount.innerHTML = data.scan_count;
}
}

function showQRresult() {
    var qrModal = new bootstrap.Modal(document.getElementById("QRmodal"));
    qrModal.show();
  }


const qrModalElement = document.getElementById("QRmodal");
qrModalElement.addEventListener("shown.bs.modal", () => {
  // Stop scanning once the modal is shown
  qrCodeScanner.stop().catch((error) => {
    console.error("Error stopping scanner:", error);
  });
});

qrModalElement.addEventListener("hidden.bs.modal", () => {
  // Resume scanning when the modal is closed
  startScanning();
});