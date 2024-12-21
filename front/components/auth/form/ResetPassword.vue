<template>
  <UForm ref="form" :state="state" :schema="schema" @submit="onSubmit">
    <ContainerVerticalInputs>
      <FormGroupPassword
        v-model="state.newPassword"
        :inputAttrs="{ autofocus: true, autocomplete: 'new-password' }"
      />
      <ButtonSubmit label="Reset my password" :status="status" block />
    </ContainerVerticalInputs>
  </UForm>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from "#ui/types"
import { z } from "zod"

const form = ref()
const status: Ref<RequestStatus> = ref("idle")

const schema = z.object({
  newPassword: z.string().min(8, "Must be at least 8 characters"),
})

const state = reactive({
  newPassword: undefined,
})

type Schema = z.output<typeof schema>

const onSubmit = async (event: FormSubmitEvent<Schema>) => {
  await myFetch(form, status)<{}>("auth/reset-password", {
    method: "post",
    body: { ...state, ...useRoute().query }, // tokenKey + newPassword
  })
  if (status.value === "success") {
    addSuccessToast("Your password has been reset. Please login with it.")
    logout(false)
  }
}
</script>
