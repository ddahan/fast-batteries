<template>
  <UForm ref="form" :state="state" :schema="schema" @submit="onSubmit" novalidate>
    <ContainerVerticalInputs>
      <FormNonFieldError :form="form" />
      <FormGroupEmail v-model="state.username" :inputAttrs="{ autofocus: true, class: 'w-full' }" />
      <FormGroupPassword
        v-model="state.password"
        :inputAttrs="{ autocomplete: 'current-password', class: 'w-full' }"
      />
      <ButtonSubmit :status="status" label="Log in" block />
    </ContainerVerticalInputs>
  </UForm>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui"
import * as z from "zod"

const form = ref()
const status: Ref<RequestStatus> = ref("idle")

const schema = z.object({
  username: z.string().email("Invalid email"),
  password: z.string(),
})

const state = reactive({
  username: "",
  password: "",
})

type Schema = z.output<typeof schema>

const onSubmit = async (event: FormSubmitEvent<Schema>) => {
  console.log(event.data)
  console.log(state)
  const token = await myFetch(form, status)<Token>("auth/access-token", {
    method: "post",
    body: new URLSearchParams(state), // required format for OAuth2
  })
  console.log(token)
  // if (token) {
  //   login(token)
  // }
}
</script>
