import { useState, useEffect } from "react";
import { getFiles, uploadFile } from "../api/files";
import type { FileItem } from "../types";

export function useFiles() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadFiles() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getFiles();
      setFiles(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load files");
    } finally {
      setIsLoading(false);
    }
  }

  async function upload(title: string, file: File) {
    const newFile = await uploadFile(title, file);
    setFiles((prev) => [newFile, ...prev]);
    return newFile;
  }

  useEffect(() => {
    loadFiles();
  }, []);

  return { files, isLoading, error, loadFiles, upload };
}