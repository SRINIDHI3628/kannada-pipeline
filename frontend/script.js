// Initialize map (Bangalore default)
const map = L.map('map').setView([12.9716, 77.5946], 13);

// Load tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap'
}).addTo(map);

// Status-based marker color
function getColor(status) {
  if (status === "Reported") return "red";
  if (status === "In Progress") return "orange";
  if (status === "Resolved") return "green";
  if (status === "Duplicate") return "gray";
  return "blue";
}

// Fetch issues from backend
fetch("http://127.0.0.1:5000/api/issues/")
  .then(res => res.json())
  .then(data => {
    data.forEach(issue => {

      const marker = L.circleMarker(
        [issue.latitude, issue.longitude],
        {
          radius: 8,
          color: getColor(issue.status)
        }
      ).addTo(map);

      marker.on("click", () => showDetails(issue));
    });
  });

// Show issue details + image + timeline
function showDetails(issue) {

  let html = `
    <p><b>Category:</b> ${issue.category}</p>
    <p><b>Status:</b> ${issue.status}</p>
    <p><b>AI Confidence:</b> ${issue.ai_confidence ?? "N/A"}</p>
  `;

  if (issue.image_path) {
    html += `<img src="../${issue.image_path}" width="100%">`;
  }

  // Fetch timeline
  fetch(`http://127.0.0.1:5000/api/issues/${issue.issue_id}/timeline`)
    .then(res => res.json())
    .then(timeline => {
      html += "<h4>Timeline</h4><ul>";
      timeline.forEach(t => {
        html += `<li>${t.old_status} → ${t.new_status} (${t.timestamp})</li>`;
      });
      html += "</ul>";

      document.getElementById("details").innerHTML = html;
    });
}
