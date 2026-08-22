const models = require('../models');

async function getAll() {
  return models.Task.findAll({
    attributes: ['id', 'title', 'done'],
    order: [['id', 'ASC']]
  });
}

module.exports = {
  getAll
};
