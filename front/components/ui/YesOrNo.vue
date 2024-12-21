<template>
  <UIcon
    :name="value ? 'i-ph-check-circle' : 'i-ph-x-circle'"
    class="size-5 bg-right-500"
    :class="{
      'bg-right-500': value,
      'bg-wrong-500': !value,
    }"
  />
</template>

<script setup lang="ts">
defineProps<{ value: boolean }>();
</script>
