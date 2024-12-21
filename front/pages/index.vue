<template>
  <UContainer class="mt-12 max-w-lg">
    <div class="flex flex-col items-center justify-center">
      <UIcon class="primary-text size-12" name="i-ph-battery-charging-vertical-bold" />
      <h1 class="text-[40px] font-bold">Fast Batteries</h1>
      <p class="text-xl font-medium tracking-tight">An opinionated template for FastAPI</p>

      <div class="mt-10 grid grid-cols-2 gap-x-8">
        <UButton
          label="Code & Doc"
          icon="i-mdi-github"
          size="xl"
          to="https://github.com/ddahan/fast-batteries"
          target="_blank"
          class="flex justify-center"
        />

        <UButton
          label="Démo"
          icon="i-ph-play-circle-bold"
          size="xl"
          to="/badges"
          class="flex justify-center"
        />
      </div>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "solo",
})
</script>
