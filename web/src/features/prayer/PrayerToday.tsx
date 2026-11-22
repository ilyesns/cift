import { Alert, Badge, Card, Group, Skeleton, Stack, Text, Title } from "@mantine/core";
import { IconInfoCircle } from "@tabler/icons-react";
import { useTranslation } from "react-i18next";
import { errorMessage } from "@/shared/api/errors";
import { useLang } from "@/shared/hooks/useLang";
import { usePrayerWindow } from "./hooks";
import classes from "./prayer.module.css";
import { findNext, formatCountdown, formatHijri, formatLongDate, formatTime } from "./time";
import { PRAYERS, type PrayerDay, type PrayerName } from "./types";

export function PrayerToday() {
  const { t } = useTranslation();
  const lang = useLang();
  const { query, now, today } = usePrayerWindow();

  if (query.isPending) return <Skeleton height={380} radius="lg" />;
  if (query.isError) {
    return (
      <Alert color="red" variant="light">
        {errorMessage(query.error)}
      </Alert>
    );
  }

  const { city, days } = query.data;
  const day = days.find((d) => d.day === today) ?? days[0];
  const next = findNext(days, now);
  const nextIsToday = next?.day.day === day.day;

  return (
    <Card padding="xl">
      <Group justify="space-between" align="flex-start" gap="lg">
        <Stack gap={2}>
          <Text size="sm" c="dimmed">
            {city.name}
          </Text>
          <Title order={2} fz={{ base: 22, sm: 26 }}>
            {formatLongDate(day.day, lang)}
          </Title>
          {day.hijri && (
            <Text c="brand" fw={600}>
              {formatHijri(day.hijri, t)}
            </Text>
          )}
        </Stack>

        {next && (
          <Stack gap={0} className={classes.next}>
            <Text size="sm" c="dimmed">
              {t("prayer.next")}
            </Text>
            <Text fw={700}>
              {t(`prayer.names.${next.entry.prayer}`)} ·{" "}
              <span className={classes.time}>
                {formatTime(next.entry.adhan, city.timezone, lang)}
              </span>
              {!nextIsToday && ` (${t("prayer.tomorrow")})`}
            </Text>
            <Text className={classes.countdown}>
              {formatCountdown(new Date(next.entry.adhan).getTime() - now.getTime())}
            </Text>
          </Stack>
        )}
      </Group>

      <Stack gap={4} mt="lg">
        {PRAYERS.map((name) => (
          <PrayerRow
            key={name}
            name={name}
            day={day}
            timeZone={city.timezone}
            isNext={nextIsToday && next?.entry.prayer === name}
          />
        ))}
      </Stack>

      {!day.complete && (
        <Alert mt="md" variant="light" color="yellow" icon={<IconInfoCircle size={18} />}>
          {t("prayer.notPublished")}
        </Alert>
      )}
    </Card>
  );
}

function PrayerRow({
  name,
  day,
  timeZone,
  isNext,
}: {
  name: PrayerName;
  day: PrayerDay;
  timeZone: string;
  isNext: boolean;
}) {
  const { t } = useTranslation();
  const lang = useLang();
  const entry = day.prayers.find((p) => p.prayer === name);
  const showJumuah = name === "dhuhr" && day.jumuah.length > 0;

  return (
    <div className={classes.row} data-next={isNext || undefined}>
      <Group justify="space-between" wrap="nowrap" gap="sm">
        <Group gap="xs" wrap="nowrap">
          <Text fw={600} className={classes.name}>
            {t(`prayer.names.${name}`)}
          </Text>
          {entry?.source === "calculated" && (
            <Badge size="xs" variant="light" color="gray">
              {t("prayer.calculated")}
            </Badge>
          )}
        </Group>
        <Group gap="md" wrap="nowrap">
          {entry?.iqama && (
            <Text size="sm" c="dimmed" className={classes.time}>
              {t("prayer.iqama")} {formatTime(entry.iqama, timeZone, lang)}
            </Text>
          )}
          <Text fw={700} fz="lg" className={classes.time}>
            {entry ? formatTime(entry.adhan, timeZone, lang) : "—"}
          </Text>
        </Group>
      </Group>
      {showJumuah && (
        <Text size="sm" c="dimmed" mt={4}>
          {t("prayer.jumuah")}: {day.jumuah.map((j) => formatTime(j, timeZone, lang)).join(" · ")}
        </Text>
      )}
    </div>
  );
}