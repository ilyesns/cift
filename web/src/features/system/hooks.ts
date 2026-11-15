import { useQuery } from "@tanstack/react-query";
import { systemApi } from "./api";

export const systemKeys = {
  all: ["system"] as const,
  liveness: () => [...systemKeys.all, "liveness"] as const,
  database: () => [...systemKeys.all, "database"] as const,
};

export function useLiveness() {
  return useQuery({
    queryKey: systemKeys.liveness(),
    queryFn: systemApi.liveness,
    retry: false,
    refetchInterval: 30_000,
  });
}

export function useDatabaseHealth() {
  return useQuery({
    queryKey: systemKeys.database(),
    queryFn: systemApi.database,
    retry: false,
    refetchInterval: 30_000,
  });
}