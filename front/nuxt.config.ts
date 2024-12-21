// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ["@nuxt/ui"],
  devtools: { enabled: true },
  ssr: false,
  app: {
    head: {
      meta: [
        {
          name: "viewport",
          content: "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no",
        },
      ],
    },
  },
  // https://nuxt.com/docs/api/composables/use-runtime-config
  runtimeConfig: {
    // Keys within public are also exposed client-side
    public: {
      backHostUrl: process.env.NUXT_BACK_HOST_URL,
      apiBase: "",
    },
  },
  typescript: {
    shim: false,
    tsConfig: {
      compilerOptions: {
        // https://nuxt.com/blog/v3-5#bundler-module-resolution
        moduleResolution: "bundler",
        paths: {
          "@": ["."],
          "@/*": ["./*"],
        },
      },
    },
  },
  tailwindcss: {
    cssPath: "~/assets/css/tailwind.css",
    configPath: "tailwind.config.ts",
  },
  compatibilityDate: "2024-04-03",
})
