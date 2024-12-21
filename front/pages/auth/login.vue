<template>
  <ContainerSingle>
    <template #title>Log in to your Account</template>
    <template #main>
      <AuthFormLogin />
      <AuthSocialDivider />
      <AuthSocialButtons />
    </template>
    <template #footer>
      <UButton to="/auth/send-reset-password-link" label="Forgot your password?" variant="ghost" />
    </template>
  </ContainerSingle>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "solo",
})

const { hasToken } = useAuthService()
if (hasToken()) {
  await navigateTo("/auth/already-logged-in")
}
</script>
