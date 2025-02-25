// Fetch the list of CSV files from the server
$.ajax({
  type: "GET", // HTTP method type for the request
  url: "/list-files", // Endpoint to fetch the list of CSV files
  dataType: "json", // Expected data type from the server
  success: function(files) { // Callback function for successful request
    // Check if any CSV files are found
    if (files.length === 0) {
      console.warn("No CSV files found."); // Log a warning if no files are found
      return; // Exit if no files are found
    }

    // Get the newest CSV file (last file in the sorted array)
    var newestFile = files[files.length - 1];

    // Fetch data from the newest CSV file
    $.ajax({
      type: "GET", // HTTP method type for the request
      url: `/EVGPTelemetry.sqlite`,
      dataType: "binary", // Expected data type from the server
      success: function(data) { // Callback function for successful request
        var lastTenEntries = getLastTenEntriesFromCSV(data); // Parse the CSV data to get the last 10 entries

        // Generate HTML content from the last 10 entries
        var htmlContent = lastTenEntries.map(entry => `<p>${entry.join(', ')}</p>`).join('');

        // Check if the HTML element with ID 'data' exists
        var dataElement = document.getElementById('data');
        if (dataElement) {
          dataElement.innerHTML = htmlContent; // Update the inner HTML with the parsed data
        } else {
          console.warn("Element with ID 'data' not found."); // Log a warning if the element is not found
        }
      },
      error: function(xhr, status, error) { // Callback function for errors
        console.log("Error fetching the CSV file: " + error); // Log the error message
      }
    });
  },
  error: function(xhr, status, error) { // Callback function for errors
    console.log("Error fetching the list of files: " + error); // Log the error message
  }
});

// Function to parse the CSV data and extract the last 10 entries
function getLastTenEntriesFromCSV(dbData) {
  // Split the CSV data into individual lines
  var lines = dbData.split('\n');

  // Remove the header line if the CSV file contains one
  // lines.shift(); // Uncomment this line if there's a header to remove

  // Extract the last 10 lines from the CSV data
  var lastTenLines = lines.slice(-11);

  // Convert each line into an array of values
  var lastTenEntries = lastTenLines.map(line => {
    return line.split(','); // Split the line by commas to get individual values
  });

  return lastTenEntries; // Return the parsed entries
}
