import { Alert, Anchor, Button, Stack, Text, TextInput } from "@mantine/core";
import { isEmail, useForm } from "@mantine/form";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { ROUTES } from "@/app/routes";
import { useForgotPassword } from "@/features/auth/hooks";
import { useLang } from "@/shared/hooks/useLang";
import { withLang } from "@/shared/lib/paths";
import { AuthCard } from "./AuthCard";

export function ForgotPasswordPage() {
  const { t } = useTranslation();
  const lang = useLang();
  const forgot = useForgotPassword();

  const form = useForm({
    mode: "uncontrolled",
    initialValues: { email: "" },
    validate: { email: isEmail(t("auth.validation.email")) },
  });

  return (
    <AuthCard title={t("auth.forgotTitle")} subtitle={t("auth.forgotSubtitle")}>
      {forgot.isSuccess ? (
        <Alert color="teal" variant="light">
          {t("auth.forgotSent")}
        </Alert>
      ) : (
        <form onSubmit={form.onSubmit((values) => forgot.mutate(values.email))}>
          <Stack>
            <TextInput
              label={t("auth.email")}
              type="email"
              autoComplete="email"
              dir="ltr"
              withAsterisk
              key={form.key("email")}
              {...form.getInputProps("email")}
            />
            <Button type="submit" loading={forgot.isPending} fullWidth>
              {t("auth.forgotSubmit")}
            </Button>
          </Stack>
        </form>
      )}
      <Text size="sm" ta="center" mt="lg">
        <Anchor component={Link} to={withLang(lang, ROUTES.signIn)}>
          {t("auth.backToSignIn")}
        </Anchor>
      </Text>
    </AuthCard>
  );
}