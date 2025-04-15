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
          size="md"
          class="ms-2"
          v-model="search"
          name="search"
          placeholder="Search owner..."
          @update:modelValue="onSearchUpdated"
          leading-icon="i-ph-magnifying-glass"
          autocomplete="off"
        >
          <template #trailing>
            <UButton
              v-if="search"
              @click="onSearchClosed"
              icon="i-ph-x-bold"
              size="xs"
              color="neutral"
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
            :items="[5, 10, 20, 50]"
            class="me-2 w-20"
            size="md"
          />
        </div>
      </div>

      <!-- Table -->
      <UTable
        :ui="{
          tbody: `transition duration-150 ease-in-out ${status == 'pending' ? 'opacity-30' : 'opacity-100'}`,
        }"
        :data="data.items"
        :columns="columns"
        empty="No badges found"
        @select="onRowSelected"
      >
        <template #owner-cell="{ row }">
          {{ row.original.owner.label }}
        </template>
        <template #expireAt-cell="{ row }">
          <UBadge
            class="px-3"
            :color="row.original.expired ? 'warning' : 'neutral'"
            variant="solid"
          >
            <div class="flex w-20 items-center justify-center gap-1">
              <UIcon
                class="shrink-0"
                :name="
                  row.original.expired ? 'i-ph-calendar-x-duotone' : 'i-ph-calendar-check-duotone'
                "
              />
              {{ dateToLabel(new Date(row.original.expireAt!)) }}
            </div>
          </UBadge>
        </template>
        <template #isActive-cell="{ row }">
          <UiYesOrNo :value="row.original.isActive" class="mt-1" />
        </template>
      </UTable>

      <!-- Number of rows & Pagination -->
      <template #footer>
        <CrudPagination v-model="page" @update:modelValue="onPageUpdated" :paginationData="data" />
      </template>
    </CrudCard>
  </div>
</template>

<script setup lang="ts">
import type { TableColumn, TableRow } from "@nuxt/ui"
import { useDebounceFn } from "@vueuse/core"

type TableBadgeOut = Pick<BadgeOut, "id" | "owner" | "expired" | "expireAt" | "isActive">

const columns: TableColumn<TableBadgeOut>[] = [
  {
    accessorKey: "owner",
    header: "Owner",
  },
  {
    accessorKey: "id",
    header: "Id",
  },
  {
    accessorKey: "expireAt",
    header: "Expiration",
  },
  {
    accessorKey: "isActive",
    header: "Active ?",
  },
]

// Query
const data: Ref<Page<BadgeOut> | undefined> = ref(undefined)
const status: Ref<RequestStatus> = ref("idle")

// Search
const search = ref("")

const page = ref(1) // display 1st page by default
const pageSize = ref(10) // display 10 results by default

const refresh = async () => {
  data.value = await myFetch(undefined, status)<Page<BadgeOut>>("badges", {
    query: {
      ...(search.value.trim() && { search: search.value }), // add search in query only if not empty
      page: page.value,
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

const onRowSelected = async (row: TableRow<TableBadgeOut>, e?: Event) => {
  await navigateTo("/badges/" + row.original.id)
}
</script>
