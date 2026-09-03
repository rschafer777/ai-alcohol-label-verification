import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StateCard } from "../src/components/StateCard";

describe("error state details", () => {
  it("shows submitted dimensions beside exact supported resize values", () => {
    render(
      <StateCard
        error={{
          requestId: "request-1",
          code: "decoded_pixel_limit",
          message: "A panel exceeds the supported decoded image dimensions.",
          retryable: true,
          fieldOrPanel: "panel-1",
          nextAction: "Resize this image to 3,464 x 2,598 pixels or smaller and retry.",
          comparisons: [
            {
              label: "Image width",
              expected: "3,464 px or fewer at this aspect ratio",
              actual: "5,712 px",
              passed: false,
            },
            {
              label: "Decoded pixels",
              expected: "12,000,000 or fewer",
              actual: "24,475,008",
              passed: false,
            },
          ],
        }}
      />,
    );

    const table = screen.getByRole("table", {
      name: "Submitted image compared with supported limits",
    });
    expect(within(table).getByText("5,712 px")).toHaveClass("fail");
    expect(within(table).getByText("24,475,008")).toHaveClass("fail");
    expect(screen.getByText(/Resize this image to 3,464 x 2,598 pixels/)).toBeInTheDocument();
  });
});
