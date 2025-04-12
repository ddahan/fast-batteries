<template>
  <div v-if="form?.getErrors('nonfield').length > 0" class="text-center text-sm text-(--ui-error)">
    {{ form.getErrors("nonfield")[0].message }}
  </div>
</template>

<script setup lang="ts">
defineProps<{ form: any }>()
</script>
