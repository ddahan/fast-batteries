<template>
  <UFormField label="Owner" name="owner">
    <USelectMenu
      arrow
      icon="i-ph-user"
      placeholder="Select a person"
      v-model="model"
      v-model:searchTerm="search"
      v-bind="inputAttrs"
      :searchable="true"
      :search-input="{
        placeholder: 'Search a name...',
        icon: 'i-lucide-search',
      }"
      ignore-filter
      :items="foundOwners"
      @update:searchTerm="debouncedSearchBadgeOwner"
    />
  </UFormField>
</template>

<script setup lang="ts">
import { useDebounceFn } from "@vueuse/core"

const model = defineModel<BadgeOwner>()
defineProps<{ inputAttrs?: Record<string, unknown> }>()

const search = ref("")
const foundOwners = ref<BadgeOwner[]>([])

const status: Ref<RequestStatus> = ref("idle")
const searchBadgeOwner = async () => {
  const data = await myFetch(undefined, status)<Page<BadgeOwner>>("users", {
    query: {
      ...(search.value.trim() && { search: search.value }), // add search in query only if not empty
      pageSize: 10,
    },
  })

  if (data) {
    foundOwners.value = data.items
  }
}

onMounted(() => searchBadgeOwner())
const debouncedSearchBadgeOwner = useDebounceFn(searchBadgeOwner, useAppConfig().defaultDebounce)
</script>
