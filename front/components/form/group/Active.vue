<template>
  <UFormGroup
    label="Active ?"
    name="isActive"
    help="Allow to disable this badge temporarily"
  >
    <UToggle v-model="model" onIcon="i-ph-check" offIcon="i-ph-x" />
  </UFormGroup>
</template>

<script setup lang="ts">
const model = defineModel<boolean>();
</script>
