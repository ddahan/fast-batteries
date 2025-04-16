<template>
  <UFormField
    label="Expiration Date"
    name="expiration"
    help="Once expired, the badge won't be usable"
  >
    <UInput
      :model-value="dateToLabel(model)"
      leading-icon="i-ph-calendar"
      trailing-icon="i-lucide:chevron-down"
      v-bind="inputAttrs"
    />
  </UFormField>
</template>

<script setup lang="ts">
const model = defineModel<Date>({ required: true })
const props = defineProps<{ inputAttrs?: Record<string, unknown> }>()
const { inputAttrs } = toRefs(props)
</script>
