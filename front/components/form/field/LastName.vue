<template>
  <UFormField class="grow" label="Last name" name="last_name" required>
    <UInput v-model="model" placeholder="Cook" icon="i-ph-user" />
  </UFormField>
</template>

<script setup lang="ts">
const model = defineModel<string>()
</script>
