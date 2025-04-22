<template>
  <ContainerSingle>
    <template #title>File Upload</template>

    <template #main>
      <form method="post" enctype="multipart/form-data">
        <ContainerVerticalInputs>
          <UButton v-if="!files" icon="i-ph-file" label="Pick files" @click="open()" block />
          <template v-if="files">
            <UCard>
              <ul class="list-none text-sm leading-5">
                <li v-for="file of files" :key="file.name">
                  {{ file.name }}
                </li>
              </ul>
            </UCard>

            <div class="flex gap-x-4">
              <UButton class="w-3/4" icon="i-ph-file-bold" block>
                <b>{{ `Upload ${files.length} ${files.length === 1 ? "file" : "files"}` }}</b>
              </UButton>
              <UButton
                class="w-1/4"
                icon="i-ph-arrow-counter-clockwise"
                variant="outline"
                label="Reset"
                :disabled="!files"
                @click="reset()"
                block
                color="neutral"
              />
            </div>
          </template>
        </ContainerVerticalInputs>
      </form>
    </template>
  </ContainerSingle>
</template>

<script setup lang="ts">
import { useFileDialog } from "@vueuse/core"

const { files, open, reset, onCancel, onChange } = useFileDialog({})

onChange((files) => {
  console.log(files)
})
</script>
