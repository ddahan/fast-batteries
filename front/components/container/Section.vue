<template>
  <div class="mt-32 md:mt-48">
    <h2 v-if="title" class="mb-6 text-center text-3xl font-bold md:mb-10 md:text-4xl">
      {{ title }}
    </h2>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{ title?: string }>();
</script>
