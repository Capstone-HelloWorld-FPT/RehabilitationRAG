import { z } from "zod";

// Messages are i18n error codes (vi.json "errors.*"), translated where they are shown.
// Backend accepts email or phone + password (BACKEND-ARCHITECTURE §6.1), so the identifier
// is only checked for being present here; the server does the real check.
export const loginSchema = z.object({
  identifier: z.string().trim().min(1, "IDENTIFIER_REQUIRED"),
  password: z.string().min(1, "PASSWORD_REQUIRED"),
});

export type LoginValues = z.infer<typeof loginSchema>;
