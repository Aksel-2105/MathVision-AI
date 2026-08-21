import { FileImage, UploadCloud } from "lucide-react";
import { useRef, useState } from "react";

import { ACCEPTED_FILE_TYPES } from "../../features/upload/validation";

type ImageDropzoneProps = { onFile: (file: File) => void; disabled?: boolean; error?: string | null };

export function ImageDropzone({ onFile, disabled = false, error }: ImageDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const chooseFile = (file: File | undefined) => { if (file && !disabled) onFile(file); };
  return <div className={`dropzone ${dragActive ? "dropzone-active" : ""} ${error ? "dropzone-error" : ""}`} onDragEnter={(event) => { event.preventDefault(); if (!disabled) setDragActive(true); }} onDragOver={(event) => event.preventDefault()} onDragLeave={(event) => { if (event.currentTarget === event.target) setDragActive(false); }} onDrop={(event) => { event.preventDefault(); setDragActive(false); chooseFile(event.dataTransfer.files[0]); }}>
    <label className="sr-only" htmlFor="image-upload-input">Choose image file</label>
    <input id="image-upload-input" ref={inputRef} className="sr-only" type="file" accept={ACCEPTED_FILE_TYPES} disabled={disabled} onChange={(event) => chooseFile(event.target.files?.[0])} />
    <div className="mx-auto grid size-14 place-items-center rounded-2xl bg-brand/10 text-brand"><UploadCloud size={27} /></div>
    <h2 className="mt-5 text-lg font-semibold text-ink">Drag and drop an image here</h2>
    <p className="mt-2 text-sm text-ink-muted">or</p>
    <button type="button" className="secondary-button mx-auto mt-4" disabled={disabled} onClick={() => inputRef.current?.click()}><FileImage size={17} />Browse files</button>
    <p className="mt-5 text-xs leading-5 text-ink-muted">PNG, JPEG, BMP, TIFF, or WEBP · Maximum 10 MB<br />Files are validated and retained temporarily for analysis.</p>
    {error && <p className="mt-4 text-sm font-medium text-red-600" role="alert">{error}</p>}
  </div>;
}
