<template>
  <ContainerSingle>
    <template #title>Create your Account</template>

    <template #main>
      <AuthFormSignup />
      <AuthSocialSeparator />
      <AuthSocialButtons />
    </template>

    <template #footer>
      <UButton label="Already a User? Log in" variant="ghost" to="/auth/login" />
    </template>
  </ContainerSingle>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "solo",
})
</script>
