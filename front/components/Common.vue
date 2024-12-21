<template>
  <div>
    <slot />
    <UNotifications />
    <Footer />
  </div>
</template>

<script setup lang="ts">
useHead({
  title: "Fast Batteries",
  htmlAttrs: { lang: "en" },
  link: [
    {
      rel: "icon",
      type: "image/svg+xml",
      href: "/favicon/battery.svg",
    },
  ],
})
</script>
