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

      <!--
      Table
      https://tanstack.com/table/latest/docs/api/features/sorting
      -->
      <UTable
        :ui="{
          tbody: `transition duration-150 ease-in-out ${status == 'pending' ? 'opacity-30' : 'opacity-100'}`,
        }"
        :data="data.items"
        :columns="columns"
        empty="No badges found"
        @select="onRowSelected"
        :state="{ sorting: sorting }"
        @update:sorting="onSortingUpdated"
        :sorting-options="{ enableSorting: true, manualSorting: true, enableSortingRemoval: true }"
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
import { h, resolveComponent } from "vue"

const UBadge = resolveComponent("UBadge")
const UButton = resolveComponent("UButton")

const columns: TableColumn<BadgeOut>[] = [
  {
    accessorKey: "owner",
    header: "Owner",
    meta: { class: { th: "w-3/12" } },
  },
  {
    accessorKey: "id",
    header: "Id",
    meta: { class: { th: "w-4/12" } },
  },
  {
    accessorKey: "expireAt",
    header: ({ column }) => {
      const isSorted = column.getIsSorted()

      return h(UButton, {
        color: "neutral",
        variant: "ghost",
        label: "Expiration",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2.5",
        onClick: column.getToggleSortingHandler(),
      })
    },
    meta: { class: { th: "w-3/12" } },
  },
  {
    accessorKey: "isActive",
    header: "Active ?",
    meta: { class: { th: "w-2/12" } },
  },
]

// Query
const data: Ref<Page<BadgeOut> | undefined> = ref(undefined)
const status: Ref<RequestStatus> = ref("idle")

// Search
const search = ref("")

// Pagination
const page = ref(1) // display 1st page by default
const pageSize = ref(10) // display 10 results by default

// Sorting
type SortingItem = { id: string; desc: boolean }
const sorting = ref([] as SortingItem[])
const backEndOrdering = ref("")

// Data fetching
const refresh = async () => {
  data.value = await myFetch(undefined, status)<Page<BadgeOut>>("badges", {
    query: {
      ...(search.value.trim() && { search: search.value }), // add search in query only if not empty
      ...(backEndOrdering.value && { ordering: backEndOrdering.value }), // add ordering in query only if not empty
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

const onSortingUpdated = (newSorting: SortingItem[]) => {
  sorting.value = newSorting

  const sort = newSorting?.[0]
  if (sort) {
    backEndOrdering.value = sort.desc ? `-${sort.id}` : sort.id
  } else {
    backEndOrdering.value = ""
  }

  page.value = 1
  refresh()
}

const onPageSizeUpdated = () => {
  page.value = 1
  refresh()
}

const onPageUpdated = () => {
  refresh()
}

// Row selection

const onRowSelected = async (row: TableRow<BadgeOut>, e?: Event) => {
  await navigateTo("/badges/" + row.original.id)
}
</script>
