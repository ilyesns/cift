import { DirectionProvider, MantineProvider } from "@mantine/core";
import { Notifications, notifications } from "@mantine/notifications";
import { MutationCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";
import i18n from "@/i18n";
import { dirFor } from "@/i18n/languages";
import { detectLang } from "@/i18n/storage";
import { ApiError } from "@/shared/api/client";
import { theme } from "@/shared/theme/theme";

function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60_000,
        refetchOnWindowFocus: false,
        retry: (failureCount, error) =>
          !(error instanceof ApiError && error.isClientError) && failureCount < 2,
      },
    },
    mutationCache: new MutationCache({
      onError: (error, _variables, _context, mutation) => {
        // A mutation can opt out with meta: { silentError: true } and handle errors itself
        if (mutation.meta?.silentError) return;
        notifications.show({
          color: "red",
          title: i18n.t("errors.title"),
          message: error instanceof ApiError ? error.message : i18n.t("errors.generic"),
        });
      },
    }),
  });
}

export function AppProviders({ children }: { children: ReactNode }) {
  const [queryClient] = useState(createQueryClient);

  return (
    <DirectionProvider initialDirection={dirFor(detectLang())} detectDirection={false}>
      <MantineProvider theme={theme} defaultColorScheme="auto">
        <Notifications position="top-center" />
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      </MantineProvider>
    </DirectionProvider>
  );
}