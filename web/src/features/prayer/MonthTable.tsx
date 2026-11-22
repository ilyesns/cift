import {
  ActionIcon,
  Alert,
  Card,
  Group,
  Skeleton,
  Table,
  Text,
  Title,
  useDirection,
} from "@mantine/core";
import { IconChevronLeft, IconChevronRight } from "@tabler/icons-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { errorMessage } from "@/shared/api/errors";
import { useLang } from "@/shared/hooks/useLang";
import { usePrayerRange } from "./hooks";
import classes from "./prayer.module.css";
import { formatMonth, formatShortDate, formatTime, isoDateIn, monthRange } from "./time";
import { DEFAULT_CITY, PRAYERS } from "./types";

interface YearMonth {
  year: number;
  month: number;
}

function shiftMonth({ year, month }: YearMonth, delta: number): YearMonth {
  const index = year * 12 + (month - 1) + delta;
  return { year: Math.floor(index / 12), month: (index % 12) + 1 };
}

export function MonthTable() {
  const { t } = useTranslation();
  const lang = useLang();
  const { dir } = useDirection();
  const today = isoDateIn(DEFAULT_CITY.timezone);

  const [current, setCurrent] = useState<YearMonth>(() => ({
    year: Number(today.slice(0, 4)),
    month: Number(today.slice(5, 7)),
  }));
  const { from, to } = monthRange(current.year, current.month);
  const query = usePrayerRange(DEFAULT_CITY.slug, from, to);

  // "Previous" points against the reading direction
  const PrevIcon = dir === "rtl" ? IconChevronRight : IconChevronLeft;
  const NextIcon = dir === "rtl" ? IconChevronLeft : IconChevronRight;
  const timeZone = query.data?.city.timezone ?? DEFAULT_CITY.timezone;
  const incomplete = query.data?.days.some((d) => !d.complete) ?? false;

  return (
    <Card padding="xl">
      <Group justify="space-between" mb="md">
        <ActionIcon
          variant="subtle"
          aria-label={t("prayer.previousMonth")}
          onClick={() => setCurrent((c) => shiftMonth(c, -1))}
        >
          <PrevIcon size={20} />
        </ActionIcon>
        <Title order={3} fz="lg" tt="capitalize">
          {t("prayer.month")} · {formatMonth(from, lang)}
        </Title>
        <ActionIcon
          variant="subtle"
          aria-label={t("prayer.nextMonth")}
          onClick={() => setCurrent((c) => shiftMonth(c, 1))}
        >
          <NextIcon size={20} />
        </ActionIcon>
      </Group>

      {incomplete && (
        <Alert variant="light" color="yellow" mb="md">
          {t("prayer.monthNotPublished")}
        </Alert>
      )}

      {query.isPending ? (
        <Skeleton height={420} />
      ) : query.isError ? (
        <Text c="red">{errorMessage(query.error)}</Text>
      ) : (
        <Table.ScrollContainer minWidth={720}>
          <Table striped highlightOnHover verticalSpacing="xs">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>{t("prayer.date")}</Table.Th>
                <Table.Th>{t("prayer.hijri")}</Table.Th>
                {PRAYERS.map((p) => (
                  <Table.Th key={p}>{t(`prayer.names.${p}`)}</Table.Th>
                ))}
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {query.data.days.map((day) => {
                const rowClass = [
                  day.day === today ? classes.today : "",
                  day.weekday === 5 ? classes.friday : "",
                ]
                  .filter(Boolean)
                  .join(" ");
                return (
                  <Table.Tr key={day.day} className={rowClass || undefined}>
                    <Table.Td>{formatShortDate(day.day, lang)}</Table.Td>
                    <Table.Td>
                      {day.hijri ? `${day.hijri.day} ${t(`hijri.m${day.hijri.month}`)}` : "—"}
                    </Table.Td>
                    {PRAYERS.map((name) => {
                      const entry = day.prayers.find((p) => p.prayer === name);
                      return (
                        <Table.Td key={name} className={classes.time}>
                          {entry ? formatTime(entry.adhan, timeZone, lang) : "—"}
                          {entry?.source === "calculated" ? "*" : ""}
                        </Table.Td>
                      );
                    })}
                  </Table.Tr>
                );
              })}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      )}
    </Card>
  );
}