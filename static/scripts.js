// console.log("script.js loaded");
// function sendText() {
//   const text = document.getElementById("text").value;
//   const form = new FormData();
//   form.append("text", text);

//   fetch("/process", { method: "POST", body: form })
//     .then(res => res.json())
//     .then(data => {
//       document.getElementById("answer").innerText = data.answer;
//       document.getElementById("audio").src = data.audio;
//     });
// }

// function record() {
//   navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
//     const recorder = new MediaRecorder(stream);
//     recorder.start();

//     setTimeout(() => recorder.stop(), 5000);

//     recorder.ondataavailable = e => {
//       const form = new FormData();
//       form.append("audio", e.data);

//       fetch("/process", { method: "POST", body: form })
//         .then(res => res.json())
//         .then(data => {
//           document.getElementById("answer").innerText = data.answer;
//           document.getElementById("audio").src = data.audio;
//         });
//     };
//   });
// }
