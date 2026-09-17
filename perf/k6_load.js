import { buildSummary, buildThresholds, readFlow } from "./lib/common.js";

// Baseline on 2026-09-16 (1 VU for 10s): p(95) = 28 ms, max = 32 ms.
// The limit leaves room for other networks and locations (e.g. the presentation room)
// while staying well below the common 500 ms target for web APIs.
const P95_LIMIT_MS = 300;

export const options = {
  scenarios: {
    constant_load: {
      executor: "constant-vus",
      vus: 10,
      duration: "30s",
    },
  },
  thresholds: buildThresholds(P95_LIMIT_MS),
};

export default function () {
  readFlow();
}

export function handleSummary(data) {
  return buildSummary("k6_load", data);
}
