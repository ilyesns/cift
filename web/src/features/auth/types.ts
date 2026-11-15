import type { Lang } from "@/i18n/languages";

export type Role = "member" | "editor" | "guide" | "admin" | "super_admin";

export interface User {
  id: string;
  email: string;
  full_name: string;
  preferred_locale: Lang;
  preferred_city: string | null;
  email_verified: boolean;
  roles: Role[];
  created_at: string;
}

export interface Session {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  user: User;
}

export interface SignInInput {
  email: string;
  password: string;
}

export interface SignUpInput extends SignInInput {
  full_name: string;
  preferred_locale: Lang;
}

export interface ProfileInput {
  full_name: string;
  preferred_locale: Lang;
  preferred_city: string | null;
}

export interface ChangePasswordInput {
  current_password: string;
  new_password: string;
}