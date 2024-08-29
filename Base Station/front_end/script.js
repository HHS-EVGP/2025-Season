$.ajax({
  type: "GET",
  url: "/2.data.csv",
  dataType: "text",
//  success: function(data) {
//    var lastTenEntries = getLastTenEntriesFromCSV(data);
//    console.log(lastTenEntries); // This will log the last 10 entries
//  },
  success: function(data) {
    var lastTenEntries = getLastTenEntriesFromCSV(data);
    // For example, display in a <div id="csvData"></div>
    var htmlContent = lastTenEntries.map(entry => `<p>${entry.join(', ')}</p>`).join('');
    document.getElementById('data').innerHTML = htmlContent;
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
