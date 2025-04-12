<template>
  <UPopover :popper="{ placement: 'bottom-start' }">
    <UButton variant="outline" color="error" label="Delete" icon="i-ph-trash" />

    <template #panel="{ close }">
      <div class="p-4">
        <div class="text-sm font-bold">Are you sure ?</div>
        <div class="mt-4 flex justify-between gap-2">
          <UButton size="sm" color="neutral" variant="ghost" @click="close"> Cancel </UButton>
          <UButton
            size="sm"
            color="error"
            :loading="status == 'pending'"
            loading-icon="i-ph-arrows-clockwise"
            :label="status == 'pending' ? '' : 'Yes, delete'"
            @click="$emit('confirm')"
            :ui="{ base: 'w-24', inline: 'justify-center' }"
          />
        </div>
      </div>
    </template>
  </UPopover>
</template>

<script setup lang="ts">
defineProps<{ status: string }>()
</script>
