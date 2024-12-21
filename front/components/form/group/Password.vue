<template>
  <UFormGroup label="Password" name="password">
    <UInput
      v-model="model"
      v-bind="inputAttrs"
      type="password"
      placeholder="••••••••••••"
      icon="i-ph-lock-simple"
    />
  </UFormGroup>
</template>

<script setup lang="ts">
const model = defineModel<string>();
const props = defineProps<{ inputAttrs?: Record<string, unknown> }>();
const { inputAttrs } = toRefs(props);
</script>
