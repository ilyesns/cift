import { Button, Stack, Text, Title } from "@mantine/core";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { useLang } from "@/shared/hooks/useLang";
import { withLang } from "@/shared/lib/paths";

export function NotFoundPage() {
  const { t } = useTranslation();
  const lang = useLang();

  return (
    <Stack gap="md" py={{ base: "xl", md: 64 }} maw={560}>
      <Text c="brand" fw={800} fz={64} lh={1}>
        404
      </Text>
      <Title order={1}>{t("notFound.title")}</Title>
      <Text c="dimmed">{t("notFound.text")}</Text>
      <Button component={Link} to={withLang(lang)} w="fit-content">
        {t("common.backHome")}
      </Button>
    </Stack>
  );
}