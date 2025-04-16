<template>
  <UForm ref="form" :state="state" :schema="schema" @submit="onSubmit" novalidate>
    <ContainerVerticalInputs>
      <ContainerHorizontalInputs>
        <FormFieldFirstName v-model="state.firstName" required class="grow" />
        <FormFieldLastName v-model="state.lastName" required class="grow" />
      </ContainerHorizontalInputs>

      <FormFieldEmail v-model="state.email" :inputAttrs="{ class: 'w-full' }" required />
      <FormFieldPassword
        v-model="state.password"
        :inputAttrs="{ autocomplete: 'new-password', class: 'w-full' }"
        required
      />
      <ButtonSubmit label="Sign Up" :status="status" block />
    </ContainerVerticalInputs>
  </UForm>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from "#ui/types"
import * as z from "zod"

const form = useTemplateRef("form")
const status: Ref<RequestStatus> = ref("idle")

const schema = z.object({
  firstName: z.string(),
  lastName: z.string(),
  email: z.string().email("Invalid email"),
  password: z.string().min(8, "Must be at least 8 characters"),
})

const state = reactive<Schema>({
  firstName: "",
  lastName: "",
  email: "",
  password: "",
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
