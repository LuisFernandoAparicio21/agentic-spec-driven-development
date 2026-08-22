const express = require('express');
const router = express.Router();
const tasksController = require('../controllers/tasks');

router.get('/', async (req, res) => {
  const tasks = await tasksController.getAll();
  res.json({ status: true, data: tasks });
});

module.exports = router;
