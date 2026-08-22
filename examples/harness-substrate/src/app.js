const express = require('express');
const app = express();

app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: true, data: { up: true } });
});

app.use('/api/tasks', require('./routes/tasks'));

app.use((req, res) => {
  res.status(404).json({ status: false, message: 'Not found' });
});

module.exports = app;
