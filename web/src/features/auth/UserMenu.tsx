import { Avatar, Button, Menu, Text, UnstyledButton } from "@mantine/core";
import { IconLogout, IconUser } from "@tabler/icons-react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router-dom";
import { ROUTES } from "@/app/routes";
import { useLang } from "@/shared/hooks/useLang";
import { withLang } from "@/shared/lib/paths";
import { useAuth } from "./AuthProvider";
import { useSignOut } from "./hooks";

export function UserMenu() {
  const { t } = useTranslation();
  const { user, status } = useAuth();
  const lang = useLang();
  const navigate = useNavigate();
  const signOut = useSignOut();

  if (status === "loading") return null;

  if (!user) {
    return (
      <Button component={Link} to={withLang(lang, ROUTES.signIn)} variant="white" size="xs">
        {t("auth.signIn")}
      </Button>
    );
  }

  return (
    <Menu position="bottom-end" width={240} withinPortal>
      <Menu.Target>
        <UnstyledButton aria-label={t("auth.account")}>
          <Avatar name={user.full_name} variant="white" color="brand" radius="xl" size={36} />
        </UnstyledButton>
      </Menu.Target>
      <Menu.Dropdown>
        <Menu.Label>
          <Text size="sm" fw={600} c="var(--mantine-color-text)" truncate>
            {user.full_name}
          </Text>
          <Text size="xs" c="dimmed" truncate dir="ltr">
            {user.email}
          </Text>
        </Menu.Label>
        <Menu.Item
          component={Link}
          to={withLang(lang, ROUTES.account)}
          leftSection={<IconUser size={16} />}
        >
          {t("auth.account")}
        </Menu.Item>
        <Menu.Divider />
        <Menu.Item
          color="red"
          leftSection={<IconLogout size={16} />}
          onClick={() => {
            // Leave protected pages first, then end the session
            navigate(withLang(lang));
            void signOut();
          }}
        >
          {t("auth.signOut")}
        </Menu.Item>
      </Menu.Dropdown>
    </Menu>
  );
}