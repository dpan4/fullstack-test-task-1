import { fetchApi } from "./config";
import type { FileItem } from "../types";

export async function getFiles(): Promise<FileItem[]> {
  return fetchApi<FileItem[]>("/files");
}

export async function uploadFile(title: string, file: File): Promise<FileItem> {
  const formData = new FormData();
  formData.append("title", title);
  formData.append("file", file);
  return fetchApi<FileItem>("/files", {
    method: "POST",
    body: formData,
  });
}

export function getDownloadUrl(fileId: string): string {
  return `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"}/files/${fileId}/download`;
}