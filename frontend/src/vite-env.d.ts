/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_AI_API_BASE_URL: string;
  readonly VITE_APP_ENV: string;
  readonly VITE_ENABLE_MOCK_AI: string;
  readonly VITE_ENABLE_REAL_TIME: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
