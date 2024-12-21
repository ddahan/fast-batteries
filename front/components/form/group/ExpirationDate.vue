<template>
  <UFormGroup
    label="Expiration Date"
    name="expiration"
    help="Once expired, the badge won't be usable"
  >
    <UPopover :popper="{ placement: 'bottom-start' }">
      <UButton
        block
        color="white"
        icon="i-ph-calendar"
        :label="dateToLabel(model)"
        :ui="{ block: 'justify-start' }"
      />

      <template #panel="{ close }">
        <LazyDatePicker v-model="model" @close="close" />
      </template>
    </UPopover>
  </UFormGroup>
</template>

<script setup lang="ts">
const model = defineModel<Date>({ required: true });
</script>
