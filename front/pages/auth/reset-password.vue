<template>
  <ContainerSingle>
    <template #title>Reset your password</template>
    <template #main>
      <AuthFormResetPassword />
    </template>
  </ContainerSingle>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: [
    (to, from) => {
      if (!to.query.hasOwnProperty("tokenKey")) {
        addErrorToast(
          "This page can't be opened directly. Please use the link directly from the received email."
        )
        return navigateTo("/auth/login")
      }
    },
  ],
})
</script>
