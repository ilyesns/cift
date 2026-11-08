import { AppShell, Box, Burger, Container, Group, Stack, useDirection } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { useEffect, useLayoutEffect } from "react";
import { useTranslation } from "react-i18next";
import { Navigate, Outlet, useLocation, useParams } from "react-router-dom";
import { applyLang } from "@/i18n";
import { dirFor, isLang } from "@/i18n/languages";
import { detectLang } from "@/i18n/storage";
import { swapLang } from "@/shared/lib/paths";
import classes from "./components/AppLayout.module.css";
import { Brand } from "./components/Brand";
import { Footer } from "./components/Footer";
import { LanguageSwitcher } from "./components/LanguageSwitcher";
import { NavItems } from "./components/NavItems";

export function AppLayout() {
  const { t } = useTranslation();
  const { lang } = useParams();
  const { pathname } = useLocation();
  const { setDirection } = useDirection();
  const [menuOpen, { toggle, close }] = useDisclosure(false);

  // Switch language and direction before paint, so Arabic never flashes left-to-right
  useLayoutEffect(() => {
    if (isLang(lang)) {
      applyLang(lang);
      setDirection(dirFor(lang));
    }
  }, [lang, setDirection]);

  // Close the phone drawer after navigating
  useEffect(() => {
    close();
  }, [pathname, close]);

  if (!isLang(lang)) {
    return <Navigate to={swapLang(pathname, detectLang())} replace />;
  }

  return (
    <AppShell
      header={{ height: 72 }}
      navbar={{ width: 280, breakpoint: "md", collapsed: { desktop: true, mobile: !menuOpen } }}
    >
      <AppShell.Header className={classes.header}>
        <Container size="lg" h="100%">
          <Group h="100%" justify="space-between" wrap="nowrap" gap="md">
            <Brand />

            <Box component="nav" aria-label={t("nav.main")} visibleFrom="md">
              <Group gap={4} wrap="nowrap">
                <NavItems variant="header" />
              </Group>
            </Box>

            <Group gap="sm" wrap="nowrap">
              <Box visibleFrom="sm">
                <LanguageSwitcher variant="header" />
              </Box>
              <Burger
                opened={menuOpen}
                onClick={toggle}
                hiddenFrom="md"
                color="white"
                size="sm"
                aria-label={t("nav.menu")}
              />
            </Group>
          </Group>
        </Container>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <Box component="nav" aria-label={t("nav.main")}>
          <Stack gap={4}>
            <NavItems variant="drawer" />
          </Stack>
        </Box>
        <Box hiddenFrom="sm" mt="xl">
          <LanguageSwitcher variant="drawer" />
        </Box>
      </AppShell.Navbar>

      <AppShell.Main className={classes.main}>
        <Container size="lg" py="xl" className={classes.content}>
          <Outlet />
        </Container>
        <Footer />
      </AppShell.Main>
    </AppShell>
  );
}