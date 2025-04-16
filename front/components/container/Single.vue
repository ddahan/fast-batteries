<template>
  <div class="mx-auto w-full sm:max-w-lg">
    <div class="text-center">
      <UIcon
        class="size-8 text-(--ui-primary) sm:size-10"
        name="i-ph:battery-charging-vertical-bold"
      />
    </div>
    <p v-if="$slots.title" class="mt-2 text-center text-2xl leading-9 font-bold tracking-tight">
      <slot name="title" />
    </p>
    <div class="mt-4 rounded-lg p-6 sm:mt-10 sm:bg-(--ui-container) sm:p-10 sm:shadow">
      <slot name="main" />
    </div>
    <div v-if="$slots.footer" class="mt-4 text-center">
      <slot name="footer" />
    </div>
  </div>
</template>
