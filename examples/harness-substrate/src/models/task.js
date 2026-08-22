const { Model, DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  class Task extends Model {}

  Task.init(
    {
      id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
      },
      title: {
        type: DataTypes.STRING(200),
        allowNull: false
      },
      done: {
        type: DataTypes.BOOLEAN,
        allowNull: false,
        defaultValue: false
      }
    },
    {
      sequelize,
      modelName: 'Task',
      tableName: 'tasks'
    }
  );

  return Task;
};
