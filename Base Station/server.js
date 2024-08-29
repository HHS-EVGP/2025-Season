const express = require('express');
const app = express();
const port = 80;

// Serve static files from the "public" directory
app.use(express.static('front_end'));

// Example API endpoint
app.get('/data', (req, res) => {
  res.json({ message: "Hello from the server!" });
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
