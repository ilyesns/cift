import { Box, Container, Group, Text } from "@mantine/core";
import { useTranslation } from "react-i18next";

export function Footer() {
  const { t } = useTranslation();
  const year = new Date().getFullYear();

  return (
    <Box component="footer" style={{ borderTop: "1px solid var(--mantine-color-default-border)" }}>
      <Container size="lg" py="lg">
        <Group justify="space-between" gap="xs">
          <Text size="sm" c="dimmed">
            © {year} {t("brand.name")}
          </Text>
          <Text size="sm" c="dimmed">
            {t("footer.rights")}
          </Text>
        </Group>
      </Container>
    </Box>
  );
}