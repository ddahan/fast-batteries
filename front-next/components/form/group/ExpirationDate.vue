<template>
  <UFormField
    label="Expiration Date"
    name="expiration"
    help="Once expired, the badge won't be usable"
  >
    <UPopover v-model:open="isCalendarOpen">
      <UButton
        color="neutral"
        block
        variant="outline"
        icon="i-ph-calendar"
        trailing-icon="i-lucide:chevron-down"
        :ui="{
          leadingIcon: 'text-(--ui-text-dimmed)',
          trailingIcon: 'text-(--ui-text-dimmed)',
          base: 'font-normal',
        }"
      >
        {{ model ? dateToLabel(model.toDate()) : "Select a date" }}
      </UButton>

      <template #content>
        <UCalendar v-model="model" class="p-2" @update:modelValue="isCalendarOpen = false" />
      </template>
    </UPopover>
  </UFormField>
</template>

<script setup lang="ts">
import { CalendarDate, fromDate } from "@internationalized/date"

const isCalendarOpen = ref(false)

const rawModel = defineModel<Date>({ required: true })
// Normalize Date → CalendarDate when receiving the value (for NuxtUI compatibility)
const model = computed({
  get: () => fromDate(rawModel.value, "UTC"),
  set: (val: CalendarDate) => {
    rawModel.value = val.toDate("UTC")
  },
})
</script>
