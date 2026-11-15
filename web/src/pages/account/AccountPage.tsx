import {
  Badge,
  Button,
  Card,
  Group,
  PasswordInput,
  Select,
  Stack,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import { hasLength, isNotEmpty, useForm } from "@mantine/form";
import { notifications } from "@mantine/notifications";
import { useTranslation } from "react-i18next";
import { useAuth } from "@/features/auth/AuthProvider";
import { useChangePassword, useUpdateProfile } from "@/features/auth/hooks";
import type { User } from "@/features/auth/types";
import { LANGUAGES, LANGUAGE_LABELS } from "@/i18n/languages";

const LANGUAGE_OPTIONS = LANGUAGES.map((lang) => ({ value: lang, label: LANGUAGE_LABELS[lang] }));

function ProfileForm({ user }: { user: User }) {
  const { t } = useTranslation();
  const update = useUpdateProfile();

  const form = useForm({
    mode: "uncontrolled",
    initialValues: {
      full_name: user.full_name,
      preferred_locale: user.preferred_locale,
      preferred_city: user.preferred_city ?? "",
    },
    validate: {
      full_name: hasLength({ min: 2, max: 120 }, t("auth.validation.nameLength")),
    },
  });

  return (
    <Card padding="xl">
      <Title order={3} fz="lg" mb="md">
        {t("account.profile")}
      </Title>
      <form
        onSubmit={form.onSubmit((values) =>
          update.mutate(
            { ...values, preferred_city: values.preferred_city.trim() || null },
            { onSuccess: () => notifications.show({ color: "teal", message: t("account.saved") }) },
          ),
        )}
      >
        <Stack>
          <TextInput
            label={t("auth.fullName")}
            withAsterisk
            key={form.key("full_name")}
            {...form.getInputProps("full_name")}
          />
          <Select
            label={t("account.preferredLanguage")}
            data={LANGUAGE_OPTIONS}
            allowDeselect={false}
            key={form.key("preferred_locale")}
            {...form.getInputProps("preferred_locale")}
          />
          <TextInput
            label={t("account.preferredCity")}
            placeholder="Firenze"
            key={form.key("preferred_city")}
            {...form.getInputProps("preferred_city")}
          />
          <Button type="submit" loading={update.isPending} w="fit-content">
            {t("account.save")}
          </Button>
        </Stack>
      </form>
    </Card>
  );
}

function PasswordForm() {
  const { t } = useTranslation();
  const change = useChangePassword();

  const form = useForm({
    mode: "uncontrolled",
    initialValues: { current_password: "", new_password: "" },
    validate: {
      current_password: isNotEmpty(t("auth.validation.required")),
      new_password: hasLength({ min: 8, max: 128 }, t("auth.validation.passwordLength")),
    },
  });

  return (
    <Card padding="xl">
      <Title order={3} fz="lg" mb="md">
        {t("account.changePassword")}
      </Title>
      <form
        onSubmit={form.onSubmit((values) =>
          change.mutate(values, {
            onSuccess: () => {
              form.reset();
              notifications.show({ color: "teal", message: t("account.passwordChanged") });
            },
          }),
        )}
      >
        <Stack>
          <PasswordInput
            label={t("auth.currentPassword")}
            autoComplete="current-password"
            withAsterisk
            key={form.key("current_password")}
            {...form.getInputProps("current_password")}
          />
          <PasswordInput
            label={t("auth.newPassword")}
            description={t("auth.validation.passwordLength")}
            autoComplete="new-password"
            withAsterisk
            key={form.key("new_password")}
            {...form.getInputProps("new_password")}
          />
          <Button type="submit" loading={change.isPending} w="fit-content">
            {t("account.changePassword")}
          </Button>
        </Stack>
      </form>
    </Card>
  );
}

export function AccountPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  if (!user) return null; // RequireAuth guarantees a user

  return (
    <Stack gap="xl" py={{ base: "md", md: 32 }} maw={720}>
      <div>
        <Title order={1}>{t("account.title")}</Title>
        <Group gap="xs" mt="xs">
          <Text c="dimmed" dir="ltr">
            {user.email}
          </Text>
          <Badge variant="light" color={user.email_verified ? "teal" : "yellow"}>
            {user.email_verified ? t("auth.verified") : t("auth.notVerified")}
          </Badge>
          {user.roles
            .filter((role) => role !== "member")
            .map((role) => (
              <Badge key={role} variant="outline">
                {t(`roles.${role}`)}
              </Badge>
            ))}
        </Group>
      </div>
      <ProfileForm user={user} />
      <PasswordForm />
    </Stack>
  );
}