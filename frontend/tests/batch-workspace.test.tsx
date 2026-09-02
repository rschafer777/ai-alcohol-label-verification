import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { BatchWorkspace } from "../src/features/batch/BatchWorkspace";

describe("batch grouping workspace", () => {
  it("requires a nonblank editable product name before confirmation", async () => {
    const user = userEvent.setup();
    const file = new File(["image"], "front.jpg", { type: "image/jpeg" });
    Object.defineProperty(file, "webkitRelativePath", {
      value: "batch/alpha/front.jpg",
    });
    render(
      <BatchWorkspace
        initialFiles={[file]}
        onFilesConsumed={vi.fn()}
        verificationClient={{ analyze: vi.fn(), verify: vi.fn() }}
      />,
    );

    const name = screen.getByLabelText("Product 1 name");
    expect(name).toHaveValue("Batch/Alpha");
    await user.clear(name);
    expect(screen.getByRole("button", { name: "Confirm as product" })).toBeDisabled();
    await user.type(name, "Cloud Nine");
    await user.click(screen.getByRole("button", { name: "Confirm as product" }));

    expect(screen.getByRole("button", { name: "Run 1 products" })).toBeEnabled();
    expect(name).toHaveValue("Cloud Nine");
  });
});
