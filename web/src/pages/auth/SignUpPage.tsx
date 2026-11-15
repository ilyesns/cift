import { Anchor, Button, PasswordInput, Stack, Text, TextInput } from "@mantine/core";
import { hasLength, isEmail, useForm } from "@mantine/form";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { ROUTES } from "@/app/routes";
import { useSignUp } from "@/features/auth/hooks";
import { useLang } from "@/shared/hooks/useLang";
import { withLang } from "@/shared/lib/paths";
import { AuthCard } from "./AuthCard";

export function SignUpPage() {
  const { t } = useTranslation();
  const lang = useLang();
  const signUp = useSignUp();

  const form = useForm({
    mode: "uncontrolled",
    initialValues: { full_name: "", email: "", password: "" },
    validate: {
      full_name: hasLength({ min: 2, max: 120 }, t("auth.validation.nameLength")),
      email: isEmail(t("auth.validation.email")),
      password: hasLength({ min: 8, max: 128 }, t("auth.validation.passwordLength")),
    },
  });

  return (
    <AuthCard title={t("auth.signUpTitle")} subtitle={t("auth.signUpSubtitle")}>
      <form
        onSubmit={form.onSubmit((values) => signUp.mutate({ ...values, preferred_locale: lang }))}
      >
        <Stack>
          <TextInput
            label={t("auth.fullName")}
            autoComplete="name"
            withAsterisk
            key={form.key("full_name")}
            {...form.getInputProps("full_name")}
          />
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
            description={t("auth.validation.passwordLength")}
            autoComplete="new-password"
            withAsterisk
            key={form.key("password")}
            {...form.getInputProps("password")}
          />
          <Button type="submit" loading={signUp.isPending} fullWidth>
            {t("auth.signUp")}
          </Button>
        </Stack>
      </form>
      <Text size="sm" ta="center" mt="lg">
        {t("auth.haveAccount")}{" "}
        <Anchor component={Link} to={withLang(lang, ROUTES.signIn)}>
          {t("auth.signIn")}
        </Anchor>
      </Text>
    </AuthCard>
  );
}