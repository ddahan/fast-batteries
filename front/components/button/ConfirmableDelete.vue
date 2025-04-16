<template>
  <UPopover arrow v-model:open="open"  :content="{
      align: 'start',
      side: 'bottom',
      sideOffset: 8
    }"">
    <UButton variant="outline" color="error" label="Delete" icon="i-ph-trash" />

    <template #content>
      <div class="p-4">
        <div class="text-sm font-bold">Are you sure ?</div>
        <div class="mt-4 flex justify-between gap-2">
          <UButton size="sm" color="neutral" variant="ghost" @click="open = false"> Cancel </UButton>
          <UButton
            size="sm"
            color="error"
            :loading="status == 'pending'"
            loading-icon="i-ph-arrows-clockwise"
            :label="status == 'pending' ? '' : 'Yes, delete'"
            @click="$emit('confirm')"
            :ui="{ base: 'w-24 justify-center' }"
          />
        </div>
      </div>
    </template>
  </UPopover>
</template>

<script setup lang="ts">
defineProps<{ status: string }>()
const open = ref(false)
</script>
