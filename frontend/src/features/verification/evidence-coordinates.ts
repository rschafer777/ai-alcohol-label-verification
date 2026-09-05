export function boundedOriginalCoordinate(
  pointer: number,
  origin: number,
  renderedSize: number,
  originalSize: number,
): number {
  if (renderedSize <= 0 || originalSize <= 1) return 0;
  return Math.round(
    Math.max(0, Math.min(originalSize - 1, ((pointer - origin) / renderedSize) * originalSize)),
  );
}
