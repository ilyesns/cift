import { api } from "@/shared/api/client";

export interface Liveness {
  status: string;
  app: string;
  environment: string;
}

export interface DatabaseHealth {
  status: string;
  database: string;
}

export const systemApi = {
  liveness: () => api.get<Liveness>("/health"),
  database: () => api.get<DatabaseHealth>("/health/db"),
};