import { Button, Card, createTheme, type MantineColorsTuple } from "@mantine/core";

// Brand magenta from the logo (#a4116a) at index 7
const brand: MantineColorsTuple = [
  "#fdf0f7",
  "#f9dcec",
  "#f2b5d6",
  "#ea8bbf",
  "#e266ab",
  "#dc4e9e",
  "#d03f93",
  "#a4116a",
  "#8a0e59",
  "#6f0a47",
];

const latin = '"Plus Jakarta Sans", "Segoe UI", system-ui, sans-serif';

export const theme = createTheme({
  primaryColor: "brand",
  primaryShade: { light: 7, dark: 5 },
  colors: { brand },
  fontFamily: latin,
  headings: { fontFamily: latin, fontWeight: "800" },
  defaultRadius: "md",
  cursorType: "pointer",
  components: {
    Card: Card.extend({ defaultProps: { radius: "lg", withBorder: true } }),
    Button: Button.extend({ defaultProps: { radius: "xl" } }),
  },
});