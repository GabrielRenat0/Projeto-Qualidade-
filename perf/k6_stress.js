import { buildSummary, buildThresholds, readFlow } from "./lib/common.js";

// The load test holds 10 VUs; this one ramps to 30 to see how the API behaves above
// that point. The limit is higher than the load test's 300 ms because degradation is
// expected here: what the test checks is that the API stays correct under pressure,
// not that it stays as fast as under nominal load.
const P95_LIMIT_MS = 500;

export const options = {
  scenarios: {
    ramping_load: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "15s", target: 15 },
        { duration: "20s", target: 30 },
        { duration: "15s", target: 30 },
        { duration: "10s", target: 0 },
      ],
      gracefulRampDown: "5s",
    },
  },
  thresholds: buildThresholds(P95_LIMIT_MS),
};

export default function () {
  readFlow();
}

export function handleSummary(data) {
  return buildSummary("k6_stress", data);
}
