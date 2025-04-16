<template>
  <UFormField label="Owner" name="owner">
    <USelectMenu
      icon="i-ph-user"
      v-model="model"
      v-bind="inputAttrs"
      :items="searchBadgeOwner"
      placeholder="Select a person"
      :search-input="{
        placeholder: 'Search a name...',
        icon: 'i-lucide-search',
      }"
      :debounce="useAppConfig().defaultDebounce"
      by="id"
    />
  </UFormField>
</template>

<script setup lang="ts">
const model = defineModel<BadgeOwner>()
const props = defineProps<{ inputAttrs?: Record<string, unknown> }>()
const { inputAttrs } = toRefs(props)

const status: Ref<RequestStatus> = ref("idle")
const searchBadgeOwner: any = async (search: string) => {
  const data = await myFetch(undefined, status)<Page<BadgeOwner>>("users", {
    query: {
      ...(search.trim() && { search: search }), // add search in query only if not empty
      pageSize: 10,
    },
  })

  if (data) {
    return data.items
  }
}
</script>
