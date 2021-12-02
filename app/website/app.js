'use strict';

// Put variables in global scope to make them available to the browser console.
const video = document.querySelector('video');
const canvas = window.canvas = document.querySelector('canvas');
canvas.width = 300;
canvas.height = 240;

const button = document.querySelector('button');
button.onclick = function() {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
  video.style.display = 'none';
  button.style.display = 'none'
};

const constraints = {
  audio: false,
  video: { facingMode: "environment"}
};

function handleSuccess(stream) {
  window.stream = stream; // make stream available to browser console
  video.srcObject = stream;
}

function handleError(error) {
  console.log('navigator.MediaDevices.getUserMedia error: ', error.message, error.name);
}

navigator.mediaDevices.getUserMedia(constraints).then(handleSuccess).catch(handleError);


function retrieve_signature() {
  var url = "https://api.crosschecker.app/signature";
  fetch(url).then(function(response) {
    if (response.ok) {
      return response.json();
    }

    return Promise.reject(response);
  }).then(function (data) {
    var date = data["date"];
    var shortDate = date.substring(0,8)
    
    var credential = `AKIA3ALIEMYGXF3P5TPZ/${shortDate}/us-east-1/s3/aws4_request`;

    document.querySelector("#x-amz-date").value = date;
    document.querySelector("#x-amz-credential").value = credential;
    document.querySelector("#policy").value = data["policy"];
    document.querySelector("#x-amz-signature").value = data["signature"];
    
  }).catch(function(error) {
    console.warn('Something went wrong',error);
  })
};
retrieve_signature();