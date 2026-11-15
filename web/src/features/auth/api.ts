import { api } from "@/shared/api/client";
import type {
  ChangePasswordInput,
  ProfileInput,
  Session,
  SignInInput,
  SignUpInput,
  User,
} from "./types";

const PUBLIC = { skipAuth: true } as const;

export const authApi = {
  signUp: (input: SignUpInput) => api.post<Session>("/auth/register", input, PUBLIC),
  signIn: (input: SignInInput) => api.post<Session>("/auth/login", input, PUBLIC),
  refresh: () => api.post<Session>("/auth/refresh", undefined, PUBLIC),
  signOut: () => api.post<void>("/auth/logout", undefined, PUBLIC),
  verifyEmail: (token: string) => api.post<User>("/auth/verify-email", { token }, PUBLIC),
  resendVerification: (email: string) =>
    api.post<{ message: string }>("/auth/resend-verification", { email }, PUBLIC),
  forgotPassword: (email: string) =>
    api.post<{ message: string }>("/auth/forgot-password", { email }, PUBLIC),
  resetPassword: (input: { token: string; password: string }) =>
    api.post<{ message: string }>("/auth/reset-password", input, PUBLIC),

  me: () => api.get<User>("/users/me"),
  updateProfile: (input: ProfileInput) => api.patch<User>("/users/me", input),
  changePassword: (input: ChangePasswordInput) => api.post<void>("/users/me/password", input),
};