<template>
  <div class="flex h-full items-center justify-between">
    <div class="flex items-center gap-3">
      <UIcon v-if="icon" :name="icon" class="size-8" />
      <h2 class="text-2xl font-semibold">{{ title }}</h2>
    </div>
    <div v-if="$slots.rightside">
      <slot name="rightside" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  icon?: string
  title: string
}>()
</script>
