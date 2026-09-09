import { fetchApi } from "./config";
import type { AlertItem } from "../types";

export async function getAlerts(): Promise<AlertItem[]> {
  return fetchApi<AlertItem[]>("/alerts");
}