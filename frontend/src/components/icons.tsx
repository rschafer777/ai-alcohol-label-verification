import type { CSSProperties, ReactElement } from "react";

/* Lucide-style line icons at stroke 1.5, ported from the approved prototype so every glyph
   matches the design pixel for pixel without a runtime dependency. */

type Shape = string | { t: "circle"; cx: number; cy: number; r: number } | { t: "rect"; x: number; y: number; width: number; height: number };

const baseStyle: CSSProperties = { display: "inline-block", verticalAlign: "-3px", flex: "none" };

function svg(shapes: Shape[], size = 16): ReactElement {
  return (
    <svg aria-hidden="true" fill="none" height={size} stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} style={baseStyle} viewBox="0 0 24 24" width={size}>
      {shapes.map((shape, index) => typeof shape === "string"
        ? <path d={shape} key={index} />
        : shape.t === "circle"
          ? <circle cx={shape.cx} cy={shape.cy} key={index} r={shape.r} />
          : <rect height={shape.height} key={index} rx={0} width={shape.width} x={shape.x} y={shape.y} />)}
    </svg>
  );
}

const c = (cx: number, cy: number, r: number): Shape => ({ t: "circle", cx, cy, r });

export const icons = {
  check: (size = 16) => svg(["M20 6 9 17l-5-5"], size),
  x: (size = 16) => svg(["M18 6 6 18", "M6 6l12 12"], size),
  minus: (size = 16) => svg(["M5 12h14"], size),
  help: (size = 16) => svg([c(12, 12, 10), "M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3", "M12 17h.01"], size),
  arrow: (size = 16) => svg(["M5 12h14", "M12 5l7 7-7 7"], size),
  back: (size = 16) => svg(["M19 12H5", "M12 19l-7-7 7-7"], size),
  image: (size = 28) => svg([{ t: "rect", x: 3, y: 3, width: 18, height: 18 }, c(9, 9, 2), "M21 15l-3.1-3.1a2 2 0 0 0-2.8 0L6 21"], size),
  imageOff: (size = 16) => svg(["M2 2l20 20", "M10.4 10.4a2 2 0 1 0 2.8 2.8", "M21 15V5a2 2 0 0 0-2-2H8", "M3 7v12a2 2 0 0 0 2 2h12"], size),
  folder: (size = 28) => svg(["M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"], size),
  table: (size = 16) => svg([{ t: "rect", x: 3, y: 4, width: 18, height: 16 }, "M3 10h18", "M3 15h18", "M9 4v16"], size),
  cards: (size = 16) => svg([{ t: "rect", x: 3, y: 3, width: 8, height: 8 }, { t: "rect", x: 13, y: 3, width: 8, height: 8 }, { t: "rect", x: 3, y: 13, width: 8, height: 8 }, { t: "rect", x: 13, y: 13, width: 8, height: 8 }], size),
  zoomIn: (size = 16) => svg([c(11, 11, 8), "M21 21l-4.3-4.3", "M11 8v6", "M8 11h6"], size),
  zoomOut: (size = 16) => svg([c(11, 11, 8), "M21 21l-4.3-4.3", "M8 11h6"], size),
  rotate: (size = 16) => svg(["M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8", "M21 3v5h-5"], size),
  sun: (size = 16) => svg([c(12, 12, 4), "M12 2v2", "M12 20v2", "M4.93 4.93l1.41 1.41", "M17.66 17.66l1.41 1.41", "M2 12h2", "M20 12h2", "M6.34 17.66l-1.41 1.41", "M19.07 4.93l-1.41 1.41"], size),
  target: (size = 14) => svg([c(12, 12, 10), c(12, 12, 6), c(12, 12, 2)], size),
  scan: (size = 16) => svg(["M3 7V5a2 2 0 0 1 2-2h2", "M17 3h2a2 2 0 0 1 2 2v2", "M21 17v2a2 2 0 0 1-2 2h-2", "M7 21H5a2 2 0 0 1-2-2v-2", "M7 12h10"], size),
  pencil: (size = 14) => svg(["M21.17 6.83 17.17 2.83a2 2 0 0 0-2.83 0L3 14.17V21h6.83L21.17 9.66a2 2 0 0 0 0-2.83Z", "m15 5 4 4"], size),
  menu: (size = 18) => svg(["M4 6h16", "M4 12h16", "M4 18h16"], size),
  keyboard: (size = 16) => svg([{ t: "rect", x: 2, y: 4, width: 20, height: 16 }, "M6 8h.01", "M10 8h.01", "M14 8h.01", "M18 8h.01", "M8 12h.01", "M12 12h.01", "M16 12h.01", "M7 16h10"], size),
  undo: (size = 16) => svg(["M3 7v6h6", "M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"], size),
  upload: (size = 20) => svg(["M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4", "M17 8l-5-5-5 5", "M12 3v12"], size),
  download: (size = 16) => svg(["M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4", "M7 10l5 5 5-5", "M12 15V3"], size),
  trash: (size = 16) => svg(["M3 6h18", "M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6", "M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"], size),
  alert: (size = 16) => svg(["M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z", "M12 9v4", "M12 17h.01"], size),
  clock: (size = 16) => svg([c(12, 12, 10), "M12 6v6l4 2"], size),
};
