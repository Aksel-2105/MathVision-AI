import { describe, expect, it } from "vitest";

import { validateImageFile } from "./validation";

describe("validateImageFile", () => {
  it("accepts a supported image under the size limit", () => {
    expect(validateImageFile(new File(["image"], "sample.png", { type: "image/png" }))).toBeNull();
  });

  it("rejects unsupported extensions and empty files", () => {
    expect(validateImageFile(new File(["text"], "sample.txt", { type: "text/plain" }))).toMatch(/unsupported/i);
    expect(validateImageFile(new File([], "empty.png", { type: "image/png" }))).toMatch(/empty/i);
  });
});
