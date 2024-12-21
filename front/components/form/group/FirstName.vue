<template>
  <UFormGroup class="grow" label="First name" name="first_name" required>
    <UInput v-model="model" placeholder="Tom" icon="i-ph-user" />
  </UFormGroup>
</template>

<script setup lang="ts">
const model = defineModel<string>();
</script>
