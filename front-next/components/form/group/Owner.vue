<template>
  <UFormField label="Owner" name="owner">
    <USelectMenu
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
      :items="foundOwners"
      :loading="status === 'pending'"
      @update:searchTerm="searchBadgeOwner"
      by="id"
    />
  </UFormField>
</template>

<script setup lang="ts">
const model = defineModel<BadgeOwner>()
const props = defineProps<{ inputAttrs?: Record<string, unknown> }>()
const { inputAttrs } = toRefs(props)

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
</script>
