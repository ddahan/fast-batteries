<template>
  <UFormField label="Active ?" name="isActive" help="Allow to disable this badge temporarily">
    <USwitch v-model="model" checkedIcon="i-ph-check" uncheckedIcon="i-ph-x" />
  </UFormField>
</template>

<script setup lang="ts">
const model = defineModel<boolean>()
</script>
