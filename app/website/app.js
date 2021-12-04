'use strict';

// Put variables in global scope to make them available to the browser console.
const video = document.querySelector('#camera');
const canvas = window.canvas = document.querySelector('#photo');
const retake = document.querySelector("#retake");
const use = document.querySelector("#use-this");

var xAmzCredential = "";
var xAmzAlgorithm = "";
var xAmzDate = "";
var policy = "";
var signature = "";

canvas.width = 300;
canvas.height = 240;

const button = document.querySelector('#take');
button.onclick = function() {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
  video.classList.add("hidden");
  button.classList.add("hidden");
  // retake.classList.remove("hidden");
  use.classList.remove("hidden");
};

function uuidv4() {
  return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  );
}

use.onclick = function() {
  var blobData = dataURItoBlob(canvas.toDataURL());

  const formData  = new FormData();
  formData.append("key", `image_uploads/${uuidv4()}.png`);
  formData.append("acl", "private");
  formData.append("Content-Type", "image/png");
  formData.append("X-Amz-Credential", xAmzCredential);
  formData.append("X-Amz-Algorithm", "AWS4-HMAC-SHA256");
  formData.append("X-Amz-Date", xAmzDate);
  formData.append("Policy", policy);
  formData.append("X-Amz-Signature", signature);
  formData.append("file", blobData);

  var url = "https://s3.amazonaws.com/crosschecker.app-data/";
  fetch(url, {
    method: 'post',
    body: formData
  }).then(function(response) {
    if (response.ok) {
      return response.json();
    }

    return Promise.reject(response);
  }).then(function (data) {
    retake.classList.add("hidden");
    use.classList.add("hidden");
    canvas.classList.add("hidden");
    console.log("returned:", data);
    
  }).catch(function(error) {
    console.warn('Something went wrong',error);
  })
}

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

    xAmzCredential = credential;
    xAmzDate = date;
    policy = data["policy"];
    signature = data["signature"]
    
  }).catch(function(error) {
    console.warn('Something went wrong',error);
  })
};
retrieve_signature();

function dataURItoBlob(dataURI) {
  // convert base64/URLEncoded data component to raw binary data held in a string
  var byteString;
  if (dataURI.split(',')[0].indexOf('base64') >= 0)
      byteString = atob(dataURI.split(',')[1]);
  else
      byteString = unescape(dataURI.split(',')[1]);

  // separate out the mime component
  var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];

  // write the bytes of the string to a typed array
  var ia = new Uint8Array(byteString.length);
  for (var i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
  }

  return new Blob([ia], {type:mimeString});
}