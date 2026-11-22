import { Stack, Text, Title } from "@mantine/core";
import { useTranslation } from "react-i18next";
import { MonthTable } from "@/features/prayer/MonthTable";
import { PrayerToday } from "@/features/prayer/PrayerToday";

export function PrayerPage() {
  const { t } = useTranslation();

  return (
    <Stack gap="xl" py={{ base: "md", md: 32 }}>
      <Stack gap={4}>
        <Title order={1}>{t("prayer.title")}</Title>
        <Text c="dimmed">{t("prayer.subtitle")}</Text>
      </Stack>
      <PrayerToday />
      <MonthTable />
      <Text size="sm" c="dimmed" maw={760}>
        {t("prayer.sourceNote")}
      </Text>
    </Stack>
  );
}