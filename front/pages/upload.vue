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
              <UButton
                class="w-3/4"
                block
                icon="i-ph-file-bold"
                :loading="status === 'pending'"
                @click="onSubmit()"
              >
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

const { files, open, reset } = useFileDialog({ accept: "*/*", multiple: true })

const status: Ref<RequestStatus> = ref("idle")

// Handle the actual upload
const onSubmit = async () => {
  if (!files.value || files.value.length === 0) return

  // build payload
  const formData = new FormData()
  for (const file of files.value) {
    formData.append("files", file) // must match FastAPI param name
  }

  await myFetch(undefined, status)("debug/upload", {
    method: "post",
    body: formData,
  })
  if (status.value === "success") {
    addSuccessToast("Your files have been upload successfully.")
    reset()
  } else {
    addErrorToast("There has been an error while uploading your files.") // TODO: improve
  }
}
</script>
