<template>
  <div>
    <CrudCard v-if="data" :withVerticalPadding="false">
      <template #header>
        <CrudHeader icon="i-ph-identification-card-bold" title="Badges">
          <template #rightside>
            <UButton label="New" to="/badges/create" icon="i-ph-plus" size="md" />
          </template>
        </CrudHeader>
      </template>
      <!-- Number of rows & Pagination -->
      <template #footer>
        <CrudPagination v-model="page" @update:modelValue="onPageUpdated" :paginationData="data" />
      </template>
    </CrudCard>
  </div>
</template>

<script setup lang="ts">
import { useDebounceFn } from "@vueuse/core"

// Sorting
const sort = ref({
  column: "id",
  direction: "asc" as "asc" | "desc",
})

const columns = [
  {
    key: "owner",
    label: "Owner",
    class: "w-3/12",
  },
  {
    key: "id",
    label: "Id",
    sortable: true,
    class: "w-4/12",
  },
  {
    key: "expireAt",
    label: "Expiration",
    sortable: true,
    class: "w-3/12",
  },
  {
    key: "isActive",
    label: "Active ?",
    class: "w-2/12",
  },
]

// Query
const data: Ref<Page<BadgeOut> | undefined> = ref(undefined)
const status: Ref<RequestStatus> = ref("idle")

// Search
const search = ref("")

const page = ref(1) // display 1st page by default
const pageSize = ref(10) // display 10 results by default
const ordering = computed(
  // Translates Nuxt UI ordering convention to back-end one
  () => (sort.value.direction === "desc" ? "-" : "") + sort.value.column
)

const refresh = async () => {
  data.value = await myFetch(undefined, status)<Page<BadgeOut>>("badges", {
    query: {
      ...(search.value.trim() && { search: search.value }), // add search in query only if not empty
      page: page.value,
      ordering: ordering.value,
      pageSize: pageSize.value,
    },
  })
}

onMounted(() => {
  refresh()
})

// Handling data refetch manually

const { defaultDebounce } = useAppConfig()
const onSearchUpdated = useDebounceFn(() => {
  page.value = 1
  refresh()
}, defaultDebounce)

const onSearchClosed = () => {
  search.value = ""
  page.value = 1
  refresh()
}

const onPageSizeUpdated = () => {
  page.value = 1
  refresh()
}

const onOrderingUpdated = () => {
  page.value = 1
  refresh()
}

const onPageUpdated = () => {
  refresh()
}

// Row selection

const onRowSelected = async (badge: BadgeOut) => {
  await navigateTo("/badges/" + badge.id)
}
</script>
