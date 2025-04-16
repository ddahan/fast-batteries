<template>
  <UForm ref="form" :state="state" :schema="schema" @submit="onSubmit" novalidate>
    <CrudCard>
      <template #header>
        <CrudHeader icon="i-ph-identification-card-bold" title="New Badge" />
      </template>

      <FormNonFieldError :form="form" />

      <ContainerVerticalInputs class="mx-auto">
        <FormFieldOwner v-model="state.owner" :inputAttrs="{ class: 'w-full' }" />
        <FormFieldExpirationDate v-model="state.expireAt" />
        <FormFieldActive v-model="state.isActive" />
      </ContainerVerticalInputs>

      <template #footer>
        <div class="flex justify-end gap-4">
          <ButtonCancel />
          <ButtonSubmit label="Create" icon="i-ph-check" :status="status" />
        </div>
      </template>
    </CrudCard>
  </UForm>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from "#ui/types"
import { z } from "zod"

const form = useTemplateRef("form")
const status: Ref<RequestStatus> = ref("idle")

const schema = z.object({
  owner: z.object({
    id: z.string(),
    label: z.string(),
  }),
  // No need to add expiration or isActive in the schema as they can't be wrong
})

const now = new Date()
const state = reactive({
  owner: undefined as BadgeOwner | undefined,
  expireAt: new Date(now.setFullYear(now.getFullYear() + 1)),
  isActive: true,
})

const onSubmit = async (event: FormSubmitEvent<z.output<typeof schema>>) => {
  await myFetch(form, status)<BadgeOut>("badges", {
    method: "post",
    body: {
      expireAt: state.expireAt,
      isActive: state.isActive,
      ownerId: state.owner?.id,
    },
  })

  if (status.value === "success") {
    addSuccessToast("New badge created")
    await navigateTo(".")
  }
}
</script>
