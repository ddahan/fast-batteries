<template>
  <UFormGroup label="Owner" name="owner">
    <USelectMenu
      icon="i-ph-user"
      v-model="model"
      :searchable="searchBadgeOwner"
      placeholder="Select a person"
      searchablePlaceholder="Search a name..."
      :debounce="useAppConfig().defaultDebounce"
      by="id"
    />
  </UFormGroup>
</template>

<script setup lang="ts">
const model = defineModel<BadgeOwner>()
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
