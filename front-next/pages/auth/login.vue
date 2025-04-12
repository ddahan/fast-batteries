<template>
  <ContainerSingle>
    <template #title>Log in to your Account</template>
    <template #main> Main </template>
    <template #footer>
      <UButton to="/auth/send-reset-password-link" label="Forgot your password?" variant="ghost" />
    </template>
  </ContainerSingle>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "solo",
})
</script>
