export const MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024;
export const ACCEPTED_FILE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"];
export const ACCEPTED_FILE_TYPES = "image/png,image/jpeg,image/bmp,image/tiff,image/webp";

export function validateImageFile(file: File): string | null {
  const extension = `.${file.name.split(".").pop()?.toLowerCase() ?? ""}`;
  if (!ACCEPTED_FILE_EXTENSIONS.includes(extension)) return "Unsupported file type. Use PNG, JPEG, BMP, TIFF, or WEBP.";
  if (file.size === 0) return "The selected file is empty.";
  if (file.size > MAX_UPLOAD_SIZE_BYTES) return "The image exceeds the 10 MB upload limit.";
  return null;
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
}
