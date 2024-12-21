<template>
  <UButton v-if="colorMode.unknown" square color="gray" size="lg" loading />
  <UButton
    v-if="!colorMode.unknown"
    variant="outline"
    square
    size="xl"
    :icon="iconMap[colorMode.preference]"
    @click="setNextColorPreference"
  />
</template>

<script setup lang="ts">
const colorMode = useColorMode()

const iconMap: any = {
  system: "i-ph-sun-dim-fill",
  dark: "i-ph-moon",
  light: "i-ph-sun",
}

const setNextColorPreference = (): void => {
  const nextColorMap: any = {
    dark: "light",
    light: "system",
    system: "dark",
  }
  colorMode.preference = nextColorMap[colorMode.preference]
}
</script>
