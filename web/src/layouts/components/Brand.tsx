import { Anchor, Group, Image, Stack, Text } from "@mantine/core";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { useLang } from "@/shared/hooks/useLang";
import { withLang } from "@/shared/lib/paths";

export function Brand() {
  const { t } = useTranslation();
  const lang = useLang();

  return (
    <Anchor component={Link} to={withLang(lang)} c="white" underline="never" miw={0}>
      <Group gap="sm" wrap="nowrap" miw={0}>
        <Image src="/logo.jpg" alt="" w={44} h={44} radius="xl" style={{ flex: "none" }} />
        <Stack gap={0} miw={0}>
          <Text fw={700} size="sm" lineClamp={1} inherit>
            {t("brand.name")}
          </Text>
          <Text size="xs" opacity={0.8} visibleFrom="xs" inherit>
            {t("brand.tagline")}
          </Text>
        </Stack>
      </Group>
    </Anchor>
  );
}