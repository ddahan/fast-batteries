<template>
  <UFormGroup label="Id" name="id">
    <UInput disabled icon="i-ph-identification-card" v-model="model" />
  </UFormGroup>
</template>

<script setup lang="ts">
const model = defineModel<string>()
</script>
