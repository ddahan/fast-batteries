<template>
  <div class="flex flex-wrap items-center justify-between" v-if="paginationData">
    <div>
      <span class="text-sm" v-if="paginationData.totalItems >= 1">
        Showing
        <span class="font-medium">{{ paginationData.startIndex }}</span>
        to
        <span class="font-medium">{{ paginationData.endIndex }}</span>
        of
        <span class="font-medium">{{ paginationData.totalItems }}</span>
        results
      </span>
    </div>
    <UPagination
      v-model="page"
      :total="paginationData.totalItems"
      :pageCount="paginationData.requestedPageSize"
      :ui="{
        wrapper: 'flex items-center gap-1',
        rounded: '!rounded-full min-w-[38px] min-h-[38px] justify-center',
        default: {
          activeButton: {
            variant: 'outline',
          },
        },
      }"
    />
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: number
  paginationData: Pagination
}>()

const emits = defineEmits(["update:modelValue"])

const page = computed({
  get: () => props.modelValue,
  set: (newPage: number) => {
    emits("update:modelValue", newPage)
  },
})
</script>
