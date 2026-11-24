import js from "@eslint/js";
import boundaries from "eslint-plugin-boundaries";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    ignores: [
      "dist",
      "coverage",
      "playwright-report",
      "test-results",
      "src/shared/api/schema.d.ts",
    ],
  },
  {
    extends: [js.configs.recommended, ...tseslint.configs.strict],
    files: ["**/*.{ts,tsx}"],
    languageOptions: { ecmaVersion: 2023, globals: globals.browser },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
      boundaries,
    },
    settings: {
      "boundaries/elements": [
        { type: "app", pattern: "src/app/**" },
        { type: "workspace", pattern: "src/workspaces/*/**", capture: ["workspace"] },
        { type: "feature", pattern: "src/features/*/**", capture: ["feature"] },
        { type: "shared", pattern: "src/shared/**" },
        { type: "test", pattern: "src/test/**" },
      ],
      "import/resolver": { typescript: { project: "./tsconfig.app.json" } },
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": ["warn", { allowConstantExport: true }],
      // FRONT-END-ARCHITECTURE section 3.1 + AGENTS.md rules 23, 27, 28
      "boundaries/element-types": [
        "error",
        {
          default: "disallow",
          rules: [
            { from: "app", allow: ["app", "workspace", "feature", "shared"] },
            {
              from: "workspace",
              allow: ["feature", "shared", ["workspace", { workspace: "${from.workspace}" }]],
            },
            { from: "feature", allow: ["feature", "shared"] },
            { from: "shared", allow: ["shared"] },
            { from: "test", allow: ["app", "workspace", "feature", "shared", "test"] },
          ],
        },
      ],
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["@/features/*/*", "**/features/*/*"],
              message: "Import another feature only through its index.ts.",
            },
          ],
        },
      ],
      "no-restricted-properties": [
        "error",
        {
          object: "window",
          property: "localStorage",
          message: "Never store tokens or patient data in localStorage.",
        },
        {
          object: "window",
          property: "sessionStorage",
          message: "Never store tokens or patient data in sessionStorage.",
        },
      ],
      "no-restricted-globals": ["error", "localStorage", "sessionStorage"],
      "no-restricted-syntax": [
        "error",
        {
          selector: "JSXAttribute[name.name='dangerouslySetInnerHTML']",
          message: "Never use dangerouslySetInnerHTML. Show AI content as sanitized Markdown.",
        },
      ],
    },
  },
);
