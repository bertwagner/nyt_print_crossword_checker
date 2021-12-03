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
  button.style.display = 'none';
  var blobData = dataURItoBlob(canvas.toDataURL());

  const formData  = new FormData();
  
  formData.append("key", "image_uploads/def.png");
  formData.append("acl", "private");
  formData.append("Content-Type", "image/png");
  formData.append("X-Amz-Credential", document.querySelector("#x-amz-credential").value);
  formData.append("X-Amz-Algorithm", "AWS4-HMAC-SHA256");
  formData.append("X-Amz-Date", document.querySelector("#x-amz-date").value);
  formData.append("Policy", document.querySelector("#policy").value);
  formData.append("X-Amz-Signature", document.querySelector("#x-amz-signature").value);
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
    console.log("returned:", data);
    
  }).catch(function(error) {
    console.warn('Something went wrong',error);
  })

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