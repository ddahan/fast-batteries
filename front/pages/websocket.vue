<template>
  <UForm :state="state" :schema="schema" @submit="onSubmit" novalidate>
    <CrudCard>
      <template #header>
        <CrudHeader icon="i-ph-bell-bold" title="Real-time Notification" />
      </template>

      <ContainerVerticalInputs class="mx-auto">
        <UFormField label="Your name" name="name">
          <UInput v-model="state.name" placeholder="Tom Cook" class="w-full" required />
        </UFormField>
        <UFormField label="Your message" name="message">
          <UTextarea
            v-model="state.message"
            placeholder="I wanted to let you know that ..."
            class="w-full"
            :rows="4"
            required
          />
        </UFormField>
      </ContainerVerticalInputs>

      <template #footer>
        <div class="flex justify-end gap-4">
          <ButtonCancel />
          <ButtonSubmit
            label="Send to all users"
            icon="i-ph-paper-plane-right-bold"
            :status="status"
          />
        </div>
      </template>
    </CrudCard>
  </UForm>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from "#ui/types"
import * as z from "zod"

const status: Ref<RequestStatus> = ref("idle")
const socket = ref<WebSocket | null>(null)

const schema = z.object({
  name: z.string().min(1, "Please enter your name"),
  message: z.string().min(1, "Please enter your message"),
})

const state = reactive({
  name: "",
  message: "",
})

const connectSocket = () => {
  const { wsHostUrl, apiBase } = useRuntimeConfig().public
  const wsUrl = process.client ? `${wsHostUrl}${apiBase}/ws/broadcast-message` : ""
  socket.value = new WebSocket(wsUrl)

  socket.value.addEventListener("message", (event) => {
    const data = JSON.parse(event.data)
    useToast().add({
      title: `New message from ${data.name}`,
      description: data.message,
      color: "info",
      icon: "i-ph-envelope",
    })
  })

  socket.value.addEventListener("close", () => {
    // Optionally reconnect or handle closure
  })
}

onMounted(() => {
  connectSocket()
})

onBeforeUnmount(() => {
  socket.value?.close()
})

const onSubmit = async (event: FormSubmitEvent<z.output<typeof schema>>) => {
  if (!socket.value || socket.value.readyState !== WebSocket.OPEN) {
    addErrorToast("WebSocket connection is not open.")
    return
  }

  status.value = "pending"

  try {
    socket.value.send(
      JSON.stringify({
        name: state.name,
        message: state.message,
      })
    )

    state.message = "" // clear message after sending
    status.value = "success"
  } catch (error) {
    status.value = "error"
  }
}
</script>
