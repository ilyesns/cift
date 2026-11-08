import {
  Badge,
  Card,
  Group,
  SimpleGrid,
  Stack,
  Text,
  ThemeIcon,
  Title,
  useDirection,
} from "@mantine/core";
import {
  IconArrowRight,
  IconBriefcase,
  IconMap2,
  IconMoonStars,
  IconNews,
} from "@tabler/icons-react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { ROUTES } from "@/app/routes";
import { useLang } from "@/shared/hooks/useLang";
import { withLang } from "@/shared/lib/paths";
import classes from "./HomePage.module.css";

const SECTIONS = [
  { key: "prayer", route: ROUTES.prayer, icon: IconMoonStars },
  { key: "news", route: ROUTES.news, icon: IconNews },
  { key: "tourism", route: ROUTES.tourism, icon: IconMap2 },
  { key: "marketplace", route: ROUTES.marketplace, icon: IconBriefcase },
] as const;

export function HomePage() {
  const { t } = useTranslation();
  const lang = useLang();
  const { dir } = useDirection();

  return (
    <Stack gap={48} py={{ base: "md", md: 40 }}>
      <Stack gap="md" maw={760}>
        <Badge variant="light" size="lg" w="fit-content">
          {t("home.eyebrow")}
        </Badge>
        <Title order={1} fz={{ base: 34, md: 52 }} lh={1.1}>
          {t("home.title")}
        </Title>
        <Text size="lg" c="dimmed" maw={620}>
          {t("home.subtitle")}
        </Text>
      </Stack>

      <SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }} spacing="lg">
        {SECTIONS.map(({ key, route, icon: Icon }) => (
          <Card
            key={key}
            component={Link}
            to={withLang(lang, route)}
            padding="xl"
            className={classes.card}
          >
            <ThemeIcon size={48} radius="md" variant="light">
              <Icon size={26} stroke={1.6} />
            </ThemeIcon>
            <Title order={3} fz="lg" mt="lg">
              {t(`home.sections.${key}.title`)}
            </Title>
            <Text size="sm" c="dimmed" mt={6}>
              {t(`home.sections.${key}.text`)}
            </Text>
            <Group gap={6} mt="lg" className={classes.more}>
              <Text size="sm" fw={600} inherit>
                {t("home.open")}
              </Text>
              {/* Arrow points in the reading direction */}
              <IconArrowRight
                size={16}
                style={{ transform: dir === "rtl" ? "scaleX(-1)" : undefined }}
              />
            </Group>
          </Card>
        ))}
      </SimpleGrid>
    </Stack>
  );
}