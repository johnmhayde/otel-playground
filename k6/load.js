import http from 'k6/http';
import { check } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const DURATION = __ENV.DURATION || '3m';

export const options = {
  scenarios: {
    root: {
      executor: 'constant-arrival-rate',
      exec: 'root',
      rate: 10,
      timeUnit: '1m',
      duration: DURATION,
      preAllocatedVUs: 1,
      maxVUs: 5,
    },
    process: {
      executor: 'constant-arrival-rate',
      exec: 'processItem',
      rate: 200,
      timeUnit: '1m',
      duration: DURATION,
      preAllocatedVUs: 5,
      maxVUs: 20,
    },
  },
};

export function root() {
  const res = http.get(`${BASE_URL}/`);
  check(res, { 'status is 200': (r) => r.status === 200 });
}

export function processItem() {
  const itemId = Math.floor(Math.random() * 10000);
  const res = http.get(`${BASE_URL}/process/${itemId}`, {
    tags: { name: '/process/{item_id}' },
  });
  check(res, { 'status is 200': (r) => r.status === 200 });
}
