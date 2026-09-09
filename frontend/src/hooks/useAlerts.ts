import { useState, useEffect } from "react";
import { getAlerts } from "../api/alerts";
import type { AlertItem } from "../types";

export function useAlerts() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadAlerts() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getAlerts();
      setAlerts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load alerts");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadAlerts();
  }, []);

  return { alerts, isLoading, error, loadAlerts };
}