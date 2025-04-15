<template>
  <div class="flex flex-wrap items-center justify-between" v-if="paginationData">
    <div>
      <span class="text-sm" v-if="paginationData.totalItems >= 1">
        Showing
        <span class="font-bold">{{ paginationData.startIndex }}</span>
        to
        <span class="font-bold">{{ paginationData.endIndex }}</span>
        of
        <span class="font-bold">{{ paginationData.totalItems }}</span>
        results
      </span>
    </div>
    <UPagination
      v-model:page="page"
      :total="paginationData.totalItems"
      :itemsPerPage="paginationData.requestedPageSize"
      :ui="{
        list: 'flex items-center gap-1',
        item: 'pagination-button',
        first: 'pagination-button',
        prev: 'pagination-button',
        next: 'pagination-button',
        last: 'pagination-button',
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
