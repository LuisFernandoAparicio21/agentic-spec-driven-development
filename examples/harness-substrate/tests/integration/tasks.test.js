// INTEGRATION test -- servidor real escuchando, DB real (sqlite),
// peticiones HTTP reales via fetch. Mismo principio que VERIFY manual
// (docs/03-runtime-verification.md): HTTP real, no mocks, no llamada
// directa a la funcion saltandose la capa de ruteo.
import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';

const app = require('../../src/app');
const db = require('../../src/models');

let server;
let baseUrl;

beforeAll(async () => {
  await db.sequelize.sync({ force: true });
  server = app.listen(0);
  const { port } = server.address();
  baseUrl = `http://127.0.0.1:${port}`;
});

afterAll(async () => {
  await db.sequelize.close();
  server.close();
});

beforeEach(async () => {
  await db.Task.destroy({ where: {}, truncate: true });
});

describe('GET /api/tasks', () => {
  it('responde 200 con status:true y data ordenada por id ascendente', async () => {
    await db.Task.bulkCreate([
      { title: 'primera tarea', done: false },
      { title: 'segunda tarea', done: true }
    ]);

    const res = await fetch(`${baseUrl}/api/tasks`);
    const body = await res.json();

    expect(res.status).toBe(200);
    expect(body.status).toBe(true);
    expect(body.data.map((t) => t.title)).toEqual(['primera tarea', 'segunda tarea']);
  });

  it('con tabla vacia responde data:[] (no null, no error)', async () => {
    const res = await fetch(`${baseUrl}/api/tasks`);
    const body = await res.json();

    expect(res.status).toBe(200);
    expect(body.status).toBe(true);
    expect(body.data).toEqual([]);
  });
});

describe('GET /health', () => {
  it('sigue respondiendo (no se rompio al agregar tasks)', async () => {
    const res = await fetch(`${baseUrl}/health`);
    const body = await res.json();

    expect(res.status).toBe(200);
    expect(body.status).toBe(true);
  });
});
