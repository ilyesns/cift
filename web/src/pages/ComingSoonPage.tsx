import { Button, Stack, Text, ThemeIcon, Title } from "@mantine/core";
import { IconTools } from "@tabler/icons-react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { useLang } from "@/shared/hooks/useLang";
import { withLang } from "@/shared/lib/paths";

export function ComingSoonPage({ titleKey }: { titleKey: string }) {
  const { t } = useTranslation();
  const lang = useLang();

  return (
    <Stack gap="md" py={{ base: "xl", md: 64 }} maw={560}>
      <ThemeIcon size={56} radius="xl" variant="light">
        <IconTools size={28} stroke={1.6} />
      </ThemeIcon>
      <Title order={1}>{t(titleKey)}</Title>
      <Text c="dimmed">{t("common.comingSoon")}</Text>
      <Button component={Link} to={withLang(lang)} variant="light" w="fit-content">
        {t("common.backHome")}
      </Button>
    </Stack>
  );
}