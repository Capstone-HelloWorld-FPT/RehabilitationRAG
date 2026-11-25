import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff } from "lucide-react";
import { useId, useState } from "react";
import { useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";

import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";

import { loginSchema, type LoginValues } from "../schemas";

type LoginFormProps = {
  // Rejects with an Error whose message is an error code (vi.json "errors.*") when login fails.
  onSubmit: (values: LoginValues) => Promise<void>;
};

export function LoginForm({ onSubmit }: LoginFormProps) {
  const { t } = useTranslation();
  const uid = useId();
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { identifier: "", password: "" },
  });

  const submit = handleSubmit(async (values) => {
    setFormError(null);
    try {
      await onSubmit(values);
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "LOGIN_UNAVAILABLE");
    }
  });

  const identifierId = `${uid}-identifier`;
  const passwordId = `${uid}-password`;
  const identifierErrorId = `${identifierId}-error`;
  const passwordErrorId = `${passwordId}-error`;

  return (
    <form onSubmit={submit} noValidate className="flex flex-col gap-4">
      {formError && (
        <p
          role="alert"
          className="border-destructive text-body-sm text-destructive rounded-sm border px-4 py-3"
        >
          {t(`errors.${formError}`)}
        </p>
      )}

      <div className="flex flex-col gap-2">
        <label htmlFor={identifierId} className="text-caption font-semibold text-teal-900">
          {t("auth.form.identifierLabel")}
        </label>
        <Input
          id={identifierId}
          autoComplete="username"
          placeholder={t("auth.form.identifierPlaceholder")}
          aria-invalid={errors.identifier ? true : undefined}
          aria-describedby={errors.identifier ? identifierErrorId : undefined}
          {...register("identifier")}
        />
        {errors.identifier?.message && (
          <p id={identifierErrorId} className="text-caption text-destructive">
            {t(`errors.${errors.identifier.message}`)}
          </p>
        )}
      </div>

      <div className="flex flex-col gap-2">
        <label htmlFor={passwordId} className="text-caption font-semibold text-teal-900">
          {t("auth.form.passwordLabel")}
        </label>
        <div className="relative">
          <Input
            id={passwordId}
            type={showPassword ? "text" : "password"}
            autoComplete="current-password"
            placeholder={t("auth.form.passwordPlaceholder")}
            className="pr-12"
            aria-invalid={errors.password ? true : undefined}
            aria-describedby={errors.password ? passwordErrorId : undefined}
            {...register("password")}
          />
          <button
            type="button"
            onClick={() => setShowPassword((shown) => !shown)}
            aria-label={showPassword ? t("auth.form.hidePassword") : t("auth.form.showPassword")}
            aria-pressed={showPassword}
            className="text-muted-foreground focus-visible:ring-ring absolute inset-y-0 right-0 flex w-12 items-center justify-center rounded-sm hover:text-teal-900 focus-visible:ring-2 focus-visible:outline-none"
          >
            {showPassword ? (
              <EyeOff aria-hidden="true" className="size-5" />
            ) : (
              <Eye aria-hidden="true" className="size-5" />
            )}
          </button>
        </div>
        {errors.password?.message && (
          <p id={passwordErrorId} className="text-caption text-destructive">
            {t(`errors.${errors.password.message}`)}
          </p>
        )}
      </div>

      <Button type="submit" variant="accent" disabled={isSubmitting} className="mt-2 h-12 w-full">
        {isSubmitting ? t("auth.form.submitting") : t("auth.form.submit")}
      </Button>
    </form>
  );
}
