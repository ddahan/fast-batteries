<template>
  <UForm :state="state" :schema="schema" @submit="onSubmit" novalidate>
    <CrudCard>
      <template #header>
        <CrudHeader icon="i-ph-arrows-left-right-bold" title="WebSocket" />
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
          <UButton type="submit" label="Send to all users" icon="i-ph-paper-plane-right-bold" />
        </div>
      </template>
    </CrudCard>
  </UForm>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from "#ui/types"
import * as z from "zod"

import { useWebSocket } from "@vueuse/core"

const { wsHostUrl, apiBase } = useRuntimeConfig().public
const { status, data, send, open, close } = useWebSocket(
  `${wsHostUrl}${apiBase}/ws/broadcast-message`,
  {
    immediate: true, // Establish the connection immediately when the composable is called
    autoClose: true, // call close() automatically when the beforeunload event is triggered
    autoReconnect: true, // reconnect on errors automatically
    heartbeat: {
      // send a small message for every given time passed to keep the connection active
      message: "ping",
      interval: 10000, // send a heartbeat message every 10 sec
      pongTimeout: 3000, // wait 3 sec for the server to reply
    },
    onMessage: (ws, event) => {
      // handle heartbeat server response (pong)

      if (event.data == "pong") {
        console.log("Websocket pong message received")
        return
      }

      const data = JSON.parse(event.data)
      useToast().add({
        title: `New message from ${data.name}`,
        description: data.message,
        color: "info",
        icon: "i-ph-envelope",
      })
    },
    onError: (ws, event) => {
      addErrorToast("WebSocket connection error")
    },
  }
)

const schema = z.object({
  name: z.string().min(1, "Please enter your name"),
  message: z.string().min(1, "Please enter your message"),
})

const state = reactive({
  name: "",
  message: "",
})

const onSubmit = async (event: FormSubmitEvent<z.output<typeof schema>>) => {
  send(JSON.stringify(state))
}
</script>
