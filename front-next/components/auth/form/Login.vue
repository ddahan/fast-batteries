<template>
  <UForm ref="form" :state="state" :schema="schema" @submit="onSubmit" novalidate>
    <ContainerVerticalInputs>
      <FormGroupEmail v-model="state.email" :inputAttrs="{ autofocus: true, class: 'w-full' }" />
      <FormGroupPassword
        v-model="state.password"
        :inputAttrs="{ autocomplete: 'current-password', class: 'w-full' }"
      />
      <ButtonSubmit :status="status" label="Log in" block />
      <FormNonFieldError :form="form" />
    </ContainerVerticalInputs>
  </UForm>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui"
import * as z from "zod"

const form = useTemplateRef("form")
const status: Ref<RequestStatus> = ref("idle")

const schema = z.object({
  email: z.string().email("Invalid email"),
  password: z.string().min(1, "Password cannot be empty"),
})

const state = reactive<Schema>({
  email: "",
  password: "",
})

type Schema = z.output<typeof schema>

const onSubmit = async (event: FormSubmitEvent<Schema>) => {
  const token = await myFetch(form, status)<Token>("auth/access-token", {
    method: "post",
    body: new URLSearchParams({
      username: state.email, // replace "email" with "username" here for OAuth2 compliance
      password: state.password,
    }),
  })
  if (token) {
    login(token)
  }
}
</script>
