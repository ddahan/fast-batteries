<template>
  <div class="mx-auto w-full sm:max-w-lg">
    <div class="text-center">
      <UIcon class="primary-text size-8 sm:size-10" name="i-ph:battery-charging-vertical-bold" />
    </div>
    <p v-if="$slots.title" class="mt-2 text-center text-2xl font-bold leading-9 tracking-tight">
      <slot name="title" />
    </p>
    <div class="mt-4 rounded-lg p-6 sm:mt-10 sm:bg-white sm:p-10 sm:shadow sm:dark:bg-gray-800">
      <slot name="main" />
    </div>
    <div v-if="$slots.footer" class="mt-4 text-center">
      <slot name="footer" />
    </div>
  </div>
</template>
