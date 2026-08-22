const app = require('../app');
const db = require('../models');

const port = process.env.PORT || 3100;

db.sequelize
  .sync()
  .then(() => {
    app.listen(port, () => {
      console.log(`harness-substrate listening on ${port}`);
    });
  })
  .catch((err) => {
    console.error('Failed to sync database', err);
    process.exit(1);
  });
