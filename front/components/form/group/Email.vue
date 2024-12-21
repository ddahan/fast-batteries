<template>
  <UFormGroup label="Email" name="email">
    <UInput
      v-model="model"
      v-bind="inputAttrs"
      placeholder="tom@example.com"
      icon="i-ph-envelope"
      type="email"
      autocomplete="email"
    />
  </UFormGroup>
</template>

<script setup lang="ts">
const model = defineModel<string>();
const props = defineProps<{ inputAttrs?: Record<string, unknown> }>();
const { inputAttrs } = toRefs(props);
</script>
