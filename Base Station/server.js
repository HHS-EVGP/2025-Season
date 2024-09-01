const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const port = 80;

// Serve static files from the "front_end" directory
app.use(express.static('front_end'));

// Endpoint to list CSV files
app.get('/list-files', (req, res) => {
  const directoryPath = path.join(__dirname, 'front_end');

  fs.readdir(directoryPath, (err, files) => {
    if (err) {
      console.error('Unable to scan directory: ' + err);
      return res.status(500).json({ error: 'Unable to scan directory' });
    }

    // Filter CSV files and sort them by their number (assuming format '001.data.csv')
    const csvFiles = files
      .filter(file => file.endsWith('.csv'))
      .sort((a, b) => {
        // Extract the numeric part from the filename and sort by it
        const numA = parseInt(a.match(/\d+/)[0], 10);
        const numB = parseInt(b.match(/\d+/)[0], 10);
        return numA - numB;
      });

    res.json(csvFiles);
  });
});

app.listen(port, () => {
  console.log(`Server started on port ${port}`);
});
