import { Maximize2 } from "lucide-react";

type ImagePreviewProps = { src: string; alt: string };

export function ImagePreview({ src, alt }: ImagePreviewProps) { return <div className="image-preview"><img src={src} alt={alt} /><span className="image-preview-label"><Maximize2 size={14} />Preview</span></div>; }
