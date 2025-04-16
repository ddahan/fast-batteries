<template>
  <div class="shadow-sm shadow-gray-200 backdrop-blur-md dark:shadow-gray-600">
    <div class="flex items-center justify-between gap-1 px-4 py-2 md:gap-2 md:px-8">
      <div class="flex h-12 cursor-pointer items-center gap-2" @click="navigateTo('/')">
        <UIcon class="h-8 w-8 text-(--ui-primary)" name="i-ph-battery-charging-vertical-bold" />
        <h1 class="text-xl font-bold">Fast Batteries</h1>
      </div>
      <div class="flex items-center gap-x-2" v-if="userProfile">
        <p class="text-sm">
          Logged as <strong>{{ userProfile.email }}</strong>
        </p>
        <UButton icon="i-ph-sign-out" variant="ghost" @click="logout()"> Log out </UButton>
      </div>
      <div class="flex gap-x-2" v-else>
        <UButton icon="i-ph-sign-in" variant="ghost" @click="navigateTo('/auth/login')">
          Log in
        </UButton>
        <UButton icon="i-ph-user-plus" variant="ghost" @click="navigateTo('/auth/signup')">
          Signup
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const userProfile = useUserProfile()
</script>
