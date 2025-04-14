<template>
  <UIcon
    :name="value ? 'i-ph-check-circle' : 'i-ph-x-circle'"
    class="size-5"
    :class="{
      'text-(--ui-success)': value,
      'text-(--ui-error)': !value,
    }"
  />
</template>

<script setup lang="ts">
defineProps<{ value: boolean }>()
</script>
