import { Alert, Button, PasswordInput, Stack } from "@mantine/core";
import { hasLength, useForm } from "@mantine/form";
import { notifications } from "@mantine/notifications";
import { useTranslation } from "react-i18next";
import { useNavigate, useSearchParams } from "react-router-dom";
import { ROUTES } from "@/app/routes";
import { useResetPassword } from "@/features/auth/hooks";
import { useLang } from "@/shared/hooks/useLang";
import { withLang } from "@/shared/lib/paths";
import { AuthCard } from "./AuthCard";

export function ResetPasswordPage() {
  const { t } = useTranslation();
  const lang = useLang();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const token = params.get("token");
  const reset = useResetPassword();

  const form = useForm({
    mode: "uncontrolled",
    initialValues: { password: "" },
    validate: {
      password: hasLength({ min: 8, max: 128 }, t("auth.validation.passwordLength")),
    },
  });

  if (!token) {
    return (
      <AuthCard title={t("auth.resetTitle")}>
        <Alert color="red" variant="light">
          {t("auth.missingToken")}
        </Alert>
      </AuthCard>
    );
  }

  return (
    <AuthCard title={t("auth.resetTitle")}>
      <form
        onSubmit={form.onSubmit((values) =>
          reset.mutate(
            { token, password: values.password },
            {
              onSuccess: () => {
                notifications.show({ color: "teal", message: t("auth.resetDone") });
                navigate(withLang(lang, ROUTES.signIn), { replace: true });
              },
            },
          ),
        )}
      >
        <Stack>
          <PasswordInput
            label={t("auth.newPassword")}
            description={t("auth.validation.passwordLength")}
            autoComplete="new-password"
            withAsterisk
            key={form.key("password")}
            {...form.getInputProps("password")}
          />
          <Button type="submit" loading={reset.isPending} fullWidth>
            {t("auth.resetSubmit")}
          </Button>
        </Stack>
      </form>
    </AuthCard>
  );
}