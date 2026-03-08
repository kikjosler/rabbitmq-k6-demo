import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 100,        // 100 виртуальных пользователей
  duration: '1m',  // 1 минута
};

const BASE_URL = 'http://localhost:8000';

export default function () {
  const order = {
    order_id: `order-${Math.random().toString(36).slice(2)}`,
    customer: `user-${__VU}`,
    amount: Math.random() * 1000
  };

  const payload = JSON.stringify(order);
  const params = {
    headers: { 'Content-Type': 'application/json' },
  };

  let res = http.post(`${BASE_URL}/orders`, payload, params);

  check(res, {
    'status is 200': (r) => r.status === 200,
    'order accepted': (r) => r.json('status') === 'order_accepted',
  });

  sleep(0.5);  // Think time
}
