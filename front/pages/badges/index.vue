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

      <!-- Filters -->
      <div class="flex items-center justify-between gap-3 px-4 py-3">
        <UInput
          size="sm"
          class="ms-2"
          v-model="search"
          name="search"
          placeholder="Search owner..."
          @update:modelValue="onSearchUpdated"
          icon="i-ph-magnifying-glass"
          autocomplete="off"
          :ui="{ icon: { trailing: { pointer: '' } } }"
        >
          <template #trailing>
            <UButton
              v-show="search !== ''"
              @click="onSearchClosed"
              icon="i-ph-x-bold"
              size="2xs"
              color="gray"
              variant="link"
              :padded="false"
            />
          </template>
        </UInput>

        <div class="flex items-center gap-1.5">
          <span class="text-sm">Rows per page:</span>
          <USelect
            v-model="pageSize"
            @update:modelValue="onPageSizeUpdated"
            :options="[5, 10, 20, 50]"
            class="me-2 w-20"
            size="sm"
          />
        </div>
      </div>

      <!-- Table -->
      <UTable
        :ui="{
          tbody: `transition duration-150 ease-in-out ${status == 'pending' ? 'opacity-30' : 'opacity-100'}`,
        }"
        v-model:sort="sort"
        @update:sort="onOrderingUpdated"
        @select="onRowSelected"
        :columns="columns"
        :rows="data.items"
        :empty-state="{
          icon: 'i-ph-list-magnifying-glass',
          label: 'No badges found',
        }"
      >
        <template #owner-data="{ row }">
          {{ row.owner.label }}
        </template>
        <template #expireAt-data="{ row }">
          <UBadge class="px-2" :color="row.expired ? 'amber' : 'gray'" size="xs" variant="solid">
            <div class="flex w-20 items-center justify-center gap-1">
              <UIcon
                class="shrink-0"
                :name="row.expired ? 'i-ph-calendar-x-duotone' : 'i-ph-calendar-check-duotone'"
              />
              {{ dateToLabel(new Date(row.expireAt)) }}
            </div>
          </UBadge>
        </template>

        <template #isActive-data="{ row }">
          <UiYesOrNo :value="row.isActive" class="mt-1" />
        </template>
      </UTable>

      <!-- Number of rows & Pagination -->
      <template #footer>
        <CrudPagination v-model="page" @update:modelValue="onPageUpdated" :paginationData="data" />
      </template>
    </CrudCard>
    <!-- <div class="flex items-center justify-center">
      <UButton size="sm" variant="outline" icon="i-ph-database-bold" color="wrong">
        Reset Data
      </UButton>
    </div> -->
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
