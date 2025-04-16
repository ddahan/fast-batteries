<template>
  <div class="mx-auto max-w-5xl p-8 md:p-12">
    <UiBaseCard>
      <!-- header -->
      <div v-if="$slots.header" class="h-24 px-6 py-4">
        <slot name="header" />
      </div>

      <!-- body -->
      <div
        class="divide-y divide-gray-200 dark:divide-gray-700"
        :class="{ 'py-8': withVerticalPadding }"
      >
        <slot />
      </div>

      <!-- footer -->
      <div v-if="$slots.footer" class="px-6 py-4">
        <slot name="footer" />
      </div>
    </UiBaseCard>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ withVerticalPadding?: boolean }>(), {
  withVerticalPadding: true,
})
</script>
