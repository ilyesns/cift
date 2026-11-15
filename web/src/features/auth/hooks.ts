import { useMutation, useQueryClient } from "@tanstack/react-query";
import { authApi } from "./api";
import { session } from "./session";

export function useSignIn() {
  return useMutation({ mutationFn: authApi.signIn, onSuccess: session.start });
}

export function useSignUp() {
  return useMutation({ mutationFn: authApi.signUp, onSuccess: session.start });
}

/** Returns a function: ends the session on the server, then locally even if the server call fails. */
export function useSignOut() {
  const queryClient = useQueryClient();
  return async () => {
    try {
      await authApi.signOut();
    } catch {
      // the local session ends either way
    }
    session.clear();
    queryClient.removeQueries();
  };
}

export function useVerifyEmail() {
  return useMutation({
    mutationFn: authApi.verifyEmail,
    meta: { silentError: true }, // the page shows its own message
    onSuccess: (user) => {
      if (session.getUser()?.id === user.id) session.setUser(user);
    },
  });
}

export function useResendVerification() {
  return useMutation({ mutationFn: authApi.resendVerification });
}

export function useForgotPassword() {
  return useMutation({ mutationFn: authApi.forgotPassword });
}

export function useResetPassword() {
  // The server ends every session on reset, so end the local one too
  return useMutation({ mutationFn: authApi.resetPassword, onSuccess: () => session.clear() });
}

export function useUpdateProfile() {
  return useMutation({ mutationFn: authApi.updateProfile, onSuccess: session.setUser });
}

export function useChangePassword() {
  return useMutation({ mutationFn: authApi.changePassword });
}