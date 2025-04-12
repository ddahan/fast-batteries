<template>
  <UButton
    type="submit"
    :loading="status == 'pending'"
    loading-icon="i-ph-arrows-clockwise"
    :label="status == 'pending' ? '' : label"
    :ui="{ base: 'min-w-32', inline: 'justify-center' }"
  />
</template>

<script setup lang="ts">
withDefaults(defineProps<{ label?: string; status: RequestStatus }>(), { label: "Validate" })
</script>
