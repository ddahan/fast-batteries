<template>
  <VCalendarDatePicker
    v-model="date"
    borderless
    :attributes="attrs"
    :is-dark="isDark"
    trim-weeks
    :first-day-of-week="2"
  />
</template>

<script setup lang="ts">
import { DatePicker as VCalendarDatePicker } from "v-calendar"
import "v-calendar/dist/style.css"

const props = defineProps<{
  modelValue?: Date
}>()

const emits = defineEmits(["update:modelValue", "close"])

const colorMode = useColorMode()

const isDark = computed(() => colorMode.value === "dark")

const date = computed({
  get: () => props.modelValue,
  set: (value) => {
    emits("update:modelValue", value)
    emits("close")
  },
})

const attrs = [
  {
    highlight: {
      color: "blue",
      class: "!bg-gray-100 dark:!bg-gray-800",
    },
    dates: new Date(),
  },
]
</script>
