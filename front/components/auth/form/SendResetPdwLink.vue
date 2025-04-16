<template>
  <UForm ref="form" :state="state" :schema="schema" @submit="onSubmit">
    <ContainerVerticalInputs>
      <FormFieldEmail v-model="state.email" :inputAttrs="{ autofocus: true, class: 'w-full' }" />
      <ButtonSubmit label="Send me reset password link" :status="status" block />
    </ContainerVerticalInputs>
  </UForm>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from "#ui/types"
import * as z from "zod"

const form = useTemplateRef("form")
const status: Ref<RequestStatus> = ref("idle")

const schema = z.object({
  email: z.string().email("Invalid email"),
})

type Schema = z.output<typeof schema>

const state = reactive<Schema>({
  email: "",
})

const onSubmit = async (event: FormSubmitEvent<Schema>) => {
  await myFetch(form, status)<{}>("auth/send-reset-password-link", {
    method: "post",
    body: state,
  })
  if (status.value === "success") {
    await navigateTo("/auth/sent-mail-confirmation")
  }
}
</script>
