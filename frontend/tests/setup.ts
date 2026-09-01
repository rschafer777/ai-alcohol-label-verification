import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(() => cleanup());

if (typeof URL.createObjectURL !== "function") {
  Object.defineProperty(URL, "createObjectURL", { value: () => "blob:test-preview", configurable: true });
}
if (typeof URL.revokeObjectURL !== "function") {
  Object.defineProperty(URL, "revokeObjectURL", { value: () => undefined, configurable: true });
}
