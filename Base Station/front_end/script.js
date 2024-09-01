$.ajax({
  type: "GET",
  url: "/001.data.csv",
  dataType: "text",
  success: function(data) {
    var lastTenEntries = getLastTenEntriesFromCSV(data);

    // For example, display in a <div id="data"></div>
    var htmlContent = lastTenEntries.map(entry => `<p>${entry.join(', ')}</p>`).join('');
    
    // Check if the element with ID 'data' exists before trying to set its innerHTML
    var dataElement = document.getElementById('data');
    if (dataElement) {
      dataElement.innerHTML = htmlContent;
    } else {
      console.warn("Element with ID 'data' not found.");
    }
  },

  error: function(xhr, status, error) {
    console.log("Error fetching the CSV file: " + error);
  }
});

function getLastTenEntriesFromCSV(csvData) {
  // Split the CSV data into lines
  var lines = csvData.split('\n');
  
  // Remove the header line if your CSV has one
  // lines.shift(); // Uncomment this if there's a header
  
  // Extract the last 10 lines
  var lastTenLines = lines.slice(-11);
  
  // Parse each of the last 10 lines into an array of values
  var lastTenEntries = lastTenLines.map(line => {
    // Assuming comma (,) is your delimiter; change if needed
    return line.split(',');
  });
  
  return lastTenEntries;
}
