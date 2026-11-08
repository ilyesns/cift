import { DirectionProvider, MantineProvider } from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";
import { dirFor } from "@/i18n/languages";
import { detectLang } from "@/i18n/storage";
import { theme } from "@/shared/theme/theme";

export function AppProviders({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { staleTime: 60_000, refetchOnWindowFocus: false, retry: 1 },
        },
      }),
  );

  return (
    <DirectionProvider initialDirection={dirFor(detectLang())} detectDirection={false}>
      <MantineProvider theme={theme} defaultColorScheme="auto">
        <Notifications position="top-center" />
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      </MantineProvider>
    </DirectionProvider>
  );
}