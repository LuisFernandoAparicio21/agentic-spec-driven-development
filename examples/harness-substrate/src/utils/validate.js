// Funcion pura reusable -- sin DB, sin Express. Candidata a unit test.
// Cuando la feature create-task se implemente via el flujo SDD real
// (spec_author -> implementer), esto es lo que un Joi schema envolveria;
// se deja como funcion pura primero porque es lo que de verdad es
// unit-testeable sin levantar nada.
function isValidTitle(title) {
  return typeof title === 'string' && title.length >= 1 && title.length <= 200;
}

module.exports = { isValidTitle };
