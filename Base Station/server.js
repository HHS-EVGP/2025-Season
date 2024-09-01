const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const port = 80;

// Set up static file serving from the "front_end" directory
app.use(express.static('front_end'));

// Endpoint to retrieve a list of CSV files in the "front_end" directory
app.get('/list-files', (req, res) => {
  const directoryPath = path.join(__dirname, 'front_end');

  // Read the contents of the directory
  fs.readdir(directoryPath, (err, files) => {
    if (err) {
      // Handle error if directory cannot be read
      console.error('Unable to scan directory: ' + err);
      return res.status(500).json({ error: 'Unable to scan directory' });
    }

    // Filter for CSV files and sort them numerically based on filename
    const csvFiles = files
      .filter(file => file.endsWith('.csv'))
      .sort((a, b) => {
        const numA = parseInt(a.match(/\d+/)[0], 10); // Extract number from filename A
        const numB = parseInt(b.match(/\d+/)[0], 10); // Extract number from filename B
        return numA - numB; // Sort files by their numeric order
      });

    // Send the sorted list of CSV files as JSON response
    res.json(csvFiles);
  });
});

// Start the Express server on the specified port
app.listen(port, () => {
  console.log(`Server started on port ${port}`);
});
