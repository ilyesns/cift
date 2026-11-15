import { ActionIcon, Badge, Card, Group, Loader, Stack, Text, Tooltip } from "@mantine/core";
import { IconRefresh } from "@tabler/icons-react";
import { useQueryClient, type UseQueryResult } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { systemKeys, useDatabaseHealth, useLiveness } from "./hooks";

function StatusRow({ label, query }: { label: string; query: UseQueryResult<unknown, Error> }) {
  const { t } = useTranslation();

  return (
    <Group justify="space-between" wrap="nowrap">
      <Text size="sm">{label}</Text>
      {query.isPending ? (
        <Badge variant="light" color="gray" leftSection={<Loader size={10} color="gray" />}>
          {t("status.checking")}
        </Badge>
      ) : query.isError ? (
        <Tooltip label={query.error.message} withArrow>
          <Badge variant="light" color="red">
            {t("status.down")}
          </Badge>
        </Tooltip>
      ) : (
        <Badge variant="light" color="teal">
          {t("status.ok")}
        </Badge>
      )}
    </Group>
  );
}

export function SystemStatus() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const liveness = useLiveness();
  const database = useDatabaseHealth();

  return (
    <Card padding="lg" maw={420}>
      <Group justify="space-between">
        <Text fw={600}>{t("status.title")}</Text>
        <ActionIcon
          variant="subtle"
          aria-label={t("status.refresh")}
          onClick={() => queryClient.invalidateQueries({ queryKey: systemKeys.all })}
        >
          <IconRefresh size={18} />
        </ActionIcon>
      </Group>
      <Stack gap="xs" mt="md">
        <StatusRow label={t("status.api")} query={liveness} />
        <StatusRow label={t("status.database")} query={database} />
      </Stack>
    </Card>
  );
}