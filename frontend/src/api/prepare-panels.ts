import { limits } from "./generated-contract";

/* Photos straight off a phone are often 24 or 48 megapixels and several megabytes, above
   the per-image limits the server enforces. The label is read from a 2-megapixel working
   image, so bringing a photo under the limit in the browser loses nothing the checks need
   and saves the reviewer a trip through an image editor. */

export interface PanelLimits {
  pixelsPerImage: number;
  fileBytes: number;
}

export interface ResizePlan {
  needed: boolean;
  width: number;
  height: number;
  reason: "pixels" | "bytes" | null;
}

/* Land a little under the pixel limit so rounding can never push a photo back over it. */
const PIXEL_HEADROOM = 0.97;
const QUALITY_LADDER = [0.92, 0.86, 0.8, 0.72];
const SHRINK_STEP = 0.85;
const MAX_ATTEMPTS = 6;
const RESIZABLE_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

export function planResize(width: number, height: number, bytes: number, panelLimits: PanelLimits = limits): ResizePlan {
  const pixels = width * height;
  if (pixels <= panelLimits.pixelsPerImage && bytes <= panelLimits.fileBytes) return { needed: false, width, height, reason: null };
  if (pixels <= panelLimits.pixelsPerImage) return { needed: true, width, height, reason: "bytes" };
  const scale = Math.sqrt((panelLimits.pixelsPerImage * PIXEL_HEADROOM) / pixels);
  return { needed: true, width: Math.max(1, Math.floor(width * scale)), height: Math.max(1, Math.floor(height * scale)), reason: "pixels" };
}

function jpegName(name: string): string {
  return `${name.replace(/\.[^.]+$/, "")}.jpg`;
}

function encode(canvas: HTMLCanvasElement, quality: number): Promise<Blob | null> {
  return new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", quality));
}

/** Bring one photo within the server's per-image limits, or return it unchanged.

    The browser decodes the photo with its EXIF orientation applied, scales it to fit the
    pixel limit while keeping its proportions, and re-encodes it as JPEG, stepping quality
    and then size down until it fits the byte limit. Where the browser cannot decode the
    file (an unsupported type, or no canvas), the file is sent as is and the server reports
    the limit with the exact resize target. */
export async function preparePanel(file: File, panelLimits: PanelLimits = limits): Promise<File> {
  if (!RESIZABLE_TYPES.has(file.type) || typeof createImageBitmap !== "function" || typeof document === "undefined") return file;
  let bitmap: ImageBitmap;
  try {
    bitmap = await createImageBitmap(file, { imageOrientation: "from-image" });
  } catch {
    return file;
  }
  try {
    const plan = planResize(bitmap.width, bitmap.height, file.size, panelLimits);
    if (!plan.needed) return file;
    let { width, height } = plan;
    for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt += 1) {
      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;
      const context = canvas.getContext("2d");
      if (!context) return file;
      context.drawImage(bitmap, 0, 0, width, height);
      for (const quality of QUALITY_LADDER) {
        const blob = await encode(canvas, quality);
        if (blob && blob.size <= panelLimits.fileBytes) return new File([blob], jpegName(file.name), { type: "image/jpeg", lastModified: file.lastModified });
      }
      width = Math.max(1, Math.floor(width * SHRINK_STEP));
      height = Math.max(1, Math.floor(height * SHRINK_STEP));
    }
    return file;
  } finally {
    bitmap.close();
  }
}

export function preparePanels(files: File[], panelLimits: PanelLimits = limits): Promise<File[]> {
  return Promise.all(files.map((file) => preparePanel(file, panelLimits)));
}
