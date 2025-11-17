function loadJSON() {
  let name = document.getElementById("inputName").value;
  let fileName = name.replace(/\s+/g, '').toLowerCase() + ".json";  // tesla car -> teslacar.json

  fetch(fileName)
    .then(response => {
      if (!response.ok) throw new Error("File not found");
      return response.json();
    })
    .then(data => {
  let html = "";

  data.forEach(item => {
    html += `
      <div style="border:1px solid black; padding:12px; margin:12px; border-radius:8px;">
        <p><strong>Application Number:</strong> ${item.application_number}</p>
        <p><strong>Title:</strong> ${item.title}</p>
        <p><strong>Abstract:</strong> ${item.abstract}</p>
        <p><strong>Similarity Score:</strong> ${item.similarity_score}</p>
      </div>
    `;
  });

  document.getElementById("output").innerHTML = html;
})

    .catch(error => {
      document.getElementById("output").textContent = "JSON file not found!";
    });
}
