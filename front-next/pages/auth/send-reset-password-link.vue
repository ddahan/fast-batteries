<template>
  <ContainerSingle>
    <template #title>Forgot your password?</template>

    <template #main>
      <AuthFormSendResetPdwLink />
    </template>
  </ContainerSingle>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "solo",
})
</script>
