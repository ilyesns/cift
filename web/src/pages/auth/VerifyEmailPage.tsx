import { Alert, Button, Group, Loader, Stack, Text } from "@mantine/core";
import { IconCircleCheck } from "@tabler/icons-react";
import { useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { Link, useSearchParams } from "react-router-dom";
import { useVerifyEmail } from "@/features/auth/hooks";
import { useLang } from "@/shared/hooks/useLang";
import { withLang } from "@/shared/lib/paths";
import { AuthCard } from "./AuthCard";

export function VerifyEmailPage() {
  const { t } = useTranslation();
  const lang = useLang();
  const [params] = useSearchParams();
  const token = params.get("token");
  const verify = useVerifyEmail();
  const started = useRef(false);

  // Tokens are single-use: guard against React StrictMode running the effect twice
  useEffect(() => {
    if (token && !started.current) {
      started.current = true;
      verify.mutate(token);
    }
  }, [token, verify]);

  let content;
  if (!token) {
    content = (
      <Alert color="red" variant="light">
        {t("auth.missingToken")}
      </Alert>
    );
  } else if (verify.isError) {
    content = (
      <Alert color="red" variant="light">
        {t("auth.verifyFailed")}
      </Alert>
    );
  } else if (verify.isSuccess) {
    content = (
      <Stack>
        <Alert color="teal" variant="light" icon={<IconCircleCheck size={18} />}>
          {t("auth.verifyDone")}
        </Alert>
        <Button component={Link} to={withLang(lang)}>
          {t("auth.goHome")}
        </Button>
      </Stack>
    );
  } else {
    content = (
      <Group>
        <Loader size="sm" />
        <Text>{t("auth.verifying")}</Text>
      </Group>
    );
  }

  return <AuthCard title={t("auth.verifyTitle")}>{content}</AuthCard>;
}