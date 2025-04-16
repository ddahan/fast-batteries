<template>
  <UFormField label="Id" name="id">
    <UInput disabled icon="i-ph-identification-card" v-model="model" v-bind="inputAttrs" />
  </UFormField>
</template>

<script setup lang="ts">
const model = defineModel<string>()
const props = defineProps<{ inputAttrs?: Record<string, unknown> }>()
const { inputAttrs } = toRefs(props)
</script>
