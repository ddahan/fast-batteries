<template>
  <ContainerSingle>
    <template #title>You're already logged in!</template>
    <template #main>
      <p class="text-center" v-if="userProfile">
        You're already logged as {{ userProfile.email }}<br />
        <strong>What do you want to do?</strong>
      </p>

      <div class="mt-6 grid grid-cols-3">
        <UButton block @click="navigateTo('/badges')">Stay logged in</UButton>
        <USeparator label="OR" orientation="vertical" />
        <UButton block @click="logout()">Log out</UButton>
      </div>
    </template>
  </ContainerSingle>
</template>

<script setup lang="ts">
const userProfile = useUserProfile()
</script>
