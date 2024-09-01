const express = require('express');
const app = express();
const port = 80;

app.use(express.static('front_end'));
app.listen(port, () => {});