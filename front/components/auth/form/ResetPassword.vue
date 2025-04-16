<template>
  <UForm ref="form" :state="state" :schema="schema" @submit="onSubmit">
    <ContainerVerticalInputs>
      <FormFieldPassword
        v-model="state.password"
        :inputAttrs="{ autofocus: true, autocomplete: 'new-password', class: 'w-full' }"
      />
      <ButtonSubmit label="Reset my password" :status="status" block />
    </ContainerVerticalInputs>
  </UForm>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from "#ui/types"
import * as z from "zod"

const form = useTemplateRef("form")
const status: Ref<RequestStatus> = ref("idle")

const schema = z.object({
  password: z.string().min(8, "Must be at least 8 characters"),
})

const state = reactive<Schema>({
  password: "",
})

type Schema = z.output<typeof schema>

const onSubmit = async (event: FormSubmitEvent<Schema>) => {
  await myFetch(form, status)<{}>("auth/reset-password", {
    method: "post",
    body: { ...state, ...useRoute().query }, // tokenKey + password
  })
  if (status.value === "success") {
    addSuccessToast("Your password has been reset. Please login with it.")
    logout(false)
  }
}
</script>
