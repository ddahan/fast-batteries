<template>
  <UForm ref="form" :state="state" :schema="schema" @submit="onSubmit">
    <ContainerVerticalInputs>
      <ContainerHorizontalInputs>
        <FormGroupFirstName v-model="state.firstName" required class="grow" />
        <FormGroupLastName v-model="state.lastName" required class="grow" />
      </ContainerHorizontalInputs>

      <FormGroupEmail v-model="state.email" required />
      <FormGroupPassword
        v-model="state.password"
        :inputAttrs="{ autocomplete: 'new-password' }"
        required
      />
      <ButtonSubmit label="Sign Up" :status="status" block />
    </ContainerVerticalInputs>
  </UForm>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from "#ui/types"
import { z } from "zod"

const form = ref()
const status: Ref<RequestStatus> = ref("idle")

const schema = z.object({
  firstName: z.string(),
  lastName: z.string(),
  email: z.string().email("Invalid email"),
  password: z.string().min(8, "Must be at least 8 characters"),
})

const state = reactive({
  firstName: undefined,
  lastName: undefined,
  email: undefined,
  password: undefined,
})

type Schema = z.output<typeof schema>

const onSubmit = async (event: FormSubmitEvent<Schema>) => {
  const user = await myFetch(form, status)<UserPublic>("users/signup", {
    method: "post",
    body: state,
  })
  if (user) {
    addSuccessToast("Account created. Please log in.")
    await navigateTo("/auth/login")
  }
}
</script>
