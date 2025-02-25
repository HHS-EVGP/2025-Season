const express = require('express');
const fs = require('fs');
const app = express();
const port = 80;

// Set up static file serving from the "front_end" directory
app.use(express.static('front_end'));

// Finding the latest csv file is no longer necessary since multiple tables can be stored in one database

// Start the Express server on the specified port
app.listen(port, () => {
  console.log(`Server started on port ${port}`);
});
