import { Alert, Button, Group, Text } from "@mantine/core";
import { IconMail } from "@tabler/icons-react";
import { useTranslation } from "react-i18next";
import { useAuth } from "./AuthProvider";
import { useResendVerification } from "./hooks";

export function VerifyEmailBanner() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const resend = useResendVerification();

  if (!user || user.email_verified) return null;

  return (
    <Alert variant="light" color="yellow" icon={<IconMail size={18} />} mb="lg">
      <Group justify="space-between" gap="sm">
        <Text size="sm">{t("auth.unverifiedBanner", { email: user.email })}</Text>
        <Button
          size="xs"
          variant="light"
          color="yellow"
          loading={resend.isPending}
          disabled={resend.isSuccess}
          onClick={() => resend.mutate(user.email)}
        >
          {resend.isSuccess ? t("auth.resent") : t("auth.resend")}
        </Button>
      </Group>
    </Alert>
  );
}