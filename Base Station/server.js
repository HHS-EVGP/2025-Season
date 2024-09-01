const express = require('express');
const app = express();
const port = 80;

// Serve static files from the "public" directory
app.use(express.static('front_end'));

app.listen(port, () => {
  console.log(`Server Started on port ${port}`);
});
