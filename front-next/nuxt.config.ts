// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  ssr: false,
  modules: ["@nuxt/ui"],
  css: ["~/assets/css/main.css"],
  // https://nuxt.com/docs/api/composables/use-runtime-config
  runtimeConfig: {
    // Keys within public are also exposed client-side
    public: {
      backHostUrl: process.env.NUXT_BACK_HOST_URL,
      apiBase: "",
    },
  },
  compatibilityDate: "2024-11-01",
})
