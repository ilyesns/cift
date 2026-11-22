import { Card, Group, Text, ThemeIcon } from "@mantine/core";
import { IconMoonStars } from "@tabler/icons-react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { ROUTES } from "@/app/routes";
import { useLang } from "@/shared/hooks/useLang";
import { withLang } from "@/shared/lib/paths";
import { usePrayerWindow } from "./hooks";
import classes from "./prayer.module.css";
import { findNext, formatCountdown, formatTime } from "./time";

export function NextPrayerCard() {
  const { t } = useTranslation();
  const lang = useLang();
  const { query, now, today } = usePrayerWindow();

  if (!query.data) return null;
  const next = findNext(query.data.days, now);
  if (!next) return null;

  const { city } = query.data;
  return (
    <Card component={Link} to={withLang(lang, ROUTES.prayer)} padding="lg" className={classes.cardLink}>
      <Group justify="space-between" gap="md">
        <Group gap="md" wrap="nowrap">
          <ThemeIcon size={48} radius="md" variant="light">
            <IconMoonStars size={26} stroke={1.6} />
          </ThemeIcon>
          <div>
            <Text size="sm" c="dimmed">
              {t("prayer.next")} · {city.name}
            </Text>
            <Text fw={700} fz="lg">
              {t(`prayer.names.${next.entry.prayer}`)}{" "}
              <span className={classes.time}>{formatTime(next.entry.adhan, city.timezone, lang)}</span>
              {next.day.day !== today && ` (${t("prayer.tomorrow")})`}
            </Text>
          </div>
        </Group>
        <Text className={classes.countdown}>
          {formatCountdown(new Date(next.entry.adhan).getTime() - now.getTime())}
        </Text>
      </Group>
    </Card>
  );
}