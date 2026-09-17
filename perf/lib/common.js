import http from "k6/http";
import { check, sleep } from "k6";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.1.0/index.js";

export const BASE_URL = __ENV.BASE_URL || "https://jsonplaceholder.typicode.com";

const RESULTS_DIR = __ENV.RESULTS_DIR || "perf/results";
const THINK_TIME_SECONDS = 1;

const READ_REQUESTS = [
  { name: "GET /posts", path: "/posts" },
  { name: "GET /posts/1", path: "/posts/1" },
  { name: "GET /comments?postId=1", path: "/comments?postId=1" },
];

export function buildThresholds(p95LimitMs) {
  const p95Limit = __ENV.P95_LIMIT_MS || p95LimitMs;

  return {
    http_req_failed: ["rate<0.01"],
    checks: ["rate>0.99"],
    http_req_duration: [`p(95)<${p95Limit}`],
  };
}

export function readFlow() {
  for (const request of READ_REQUESTS) {
    const response = http.get(`${BASE_URL}${request.path}`, {
      tags: { name: request.name },
    });
    check(response, {
      [`${request.name} status is 200`]: (r) => r.status === 200,
    });
  }

  sleep(THINK_TIME_SECONDS);
}

export function buildSummary(testName, data) {
  return {
    stdout: textSummary(data, { indent: " ", enableColors: true }),
    [`${RESULTS_DIR}/${testName}_summary.json`]: JSON.stringify(data, null, 2),
  };
}
