import { Card, Center, Stack, Text, Title } from "@mantine/core";
import type { ReactNode } from "react";

export function AuthCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  return (
    <Center py={{ base: "md", md: 48 }}>
      <Card w="100%" maw={440} padding="xl" shadow="sm">
        <Stack gap={4} mb="lg">
          <Title order={2}>{title}</Title>
          {subtitle && (
            <Text c="dimmed" size="sm">
              {subtitle}
            </Text>
          )}
        </Stack>
        {children}
      </Card>
    </Center>
  );
}