import type { ReactElement } from "react";

/** Four 11 px registration marks drawn just outside a `.blueprint` frame. */
export function Corners(): ReactElement {
  return (
    <>
      <i aria-hidden="true" className="corner tl" />
      <i aria-hidden="true" className="corner tr" />
      <i aria-hidden="true" className="corner bl" />
      <i aria-hidden="true" className="corner br" />
    </>
  );
}
