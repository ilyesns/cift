import { SegmentedControl } from "@mantine/core";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router-dom";
import { LANGUAGES, LANGUAGE_LABELS, isLang } from "@/i18n/languages";
import { useLang } from "@/shared/hooks/useLang";
import { swapLang } from "@/shared/lib/paths";
import classes from "./LanguageSwitcher.module.css";

const OPTIONS = LANGUAGES.map((lang) => ({ value: lang, label: LANGUAGE_LABELS[lang] }));

export function LanguageSwitcher({ variant }: { variant: "header" | "drawer" }) {
  const { t } = useTranslation();
  const current = useLang();
  const { pathname } = useLocation();
  const navigate = useNavigate();

  return (
    <SegmentedControl
      aria-label={t("nav.language")}
      data={OPTIONS}
      value={current}
      onChange={(value) => {
        if (isLang(value)) navigate(swapLang(pathname, value));
      }}
      size="xs"
      radius="xl"
      fullWidth={variant === "drawer"}
      classNames={variant === "header" ? classes : undefined}
    />
  );
}