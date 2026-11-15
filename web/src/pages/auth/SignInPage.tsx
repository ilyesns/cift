import { Anchor, Button, Group, PasswordInput, Stack, Text, TextInput } from "@mantine/core";
import { isEmail, isNotEmpty, useForm } from "@mantine/form";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { ROUTES } from "@/app/routes";
import { useSignIn } from "@/features/auth/hooks";
import { useLang } from "@/shared/hooks/useLang";
import { withLang } from "@/shared/lib/paths";
import { AuthCard } from "./AuthCard";

export function SignInPage() {
  const { t } = useTranslation();
  const lang = useLang();
  const signIn = useSignIn();

  const form = useForm({
    mode: "uncontrolled",
    initialValues: { email: "", password: "" },
    validate: {
      email: isEmail(t("auth.validation.email")),
      password: isNotEmpty(t("auth.validation.required")),
    },
  });

  // After success, GuestOnly sends the user back to where they were going
  return (
    <AuthCard title={t("auth.signInTitle")} subtitle={t("auth.signInSubtitle")}>
      <form onSubmit={form.onSubmit((values) => signIn.mutate(values))}>
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
          <PasswordInput
            label={t("auth.password")}
            autoComplete="current-password"
            withAsterisk
            key={form.key("password")}
            {...form.getInputProps("password")}
          />
          <Group justify="flex-end">
            <Anchor component={Link} to={withLang(lang, ROUTES.forgotPassword)} size="sm">
              {t("auth.forgotLink")}
            </Anchor>
          </Group>
          <Button type="submit" loading={signIn.isPending} fullWidth>
            {t("auth.signIn")}
          </Button>
        </Stack>
      </form>
      <Text size="sm" ta="center" mt="lg">
        {t("auth.noAccount")}{" "}
        <Anchor component={Link} to={withLang(lang, ROUTES.signUp)}>
          {t("auth.signUp")}
        </Anchor>
      </Text>
    </AuthCard>
  );
}