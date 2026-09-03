import { useEffect, useMemo, type ReactElement } from "react";

export function FilePreview({ file, alt = "", className }: { file: File; alt?: string; className?: string }): ReactElement {
  const url = useMemo(() => URL.createObjectURL(file), [file]);
  useEffect(() => () => URL.revokeObjectURL(url), [url]);
  return <img alt={alt} className={className} src={url} />;
}
