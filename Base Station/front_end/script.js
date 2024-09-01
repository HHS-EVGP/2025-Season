// Fetch the list of CSV files first
$.ajax({
  type: "GET",
  url: "/list-files", // This endpoint should return a list of files
  dataType: "json",
  success: function(files) {
    // Assuming the files are sorted and named '001.data.csv' to '999.data.csv'
    if (files.length === 0) {
      console.warn("No CSV files found.");
      return;
    }

    // Get the newest file (the last file in the sorted array)
    var newestFile = files[files.length - 1];

    // Fetch the data from the newest file
    $.ajax({
      type: "GET",
      url: `/${newestFile}`,
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
  },
  error: function(xhr, status, error) {
    console.log("Error fetching the list of files: " + error);
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
