<template>
  <UIcon v-if="iconName" :name="iconName" :class="iconClass" class="size-5" />
</template>

<script setup lang="ts">
import { useTimeoutFn } from "@vueuse/core"

const props = defineProps<{ status: any }>()
const { defaultHide } = useAppConfig()

const iconName = ref("")
const iconClass = ref("")

watch(
  () => props.status,
  (newStatus: any) => {
    if (newStatus === "pending") {
      iconName.value = "i-ph-arrows-clockwise"
      iconClass.value = "text-gray-400 dark:text-gray-500 animate-spin"
    }
    if (newStatus === "success") {
      iconName.value = "i-ph-check-bold"
      iconClass.value = "text-right-500"
    }
    if (newStatus === "error") {
      iconName.value = "i-ph-x-bold"
      iconClass.value = "text-wrong-500"
    }
    useTimeoutFn(() => {
      iconName.value = ""
    }, defaultHide)
  }
)
</script>
