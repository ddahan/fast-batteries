<template>
  <UFormGroup class="grow" label="Last name" name="last_name" required>
    <UInput v-model="model" placeholder="Cook" icon="i-ph-user" />
  </UFormGroup>
</template>

<script setup lang="ts">
const model = defineModel<string>();
</script>
