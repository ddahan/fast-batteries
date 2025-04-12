<template>
  <div class="flex gap-2">
    <UButton
      block
      class="shrink"
      v-for="network in networks"
      color="neutral"
      :label="`${network.name}`"
      :icon="network.icon"
      @click="login(network.slug)"
    />
  </div>
</template>

<script setup lang="ts">
const networks = [
  { name: "Github", icon: "i-bxl-github", slug: "github" },
  { name: "Linked In", icon: "i-bxl-linkedin-square", slug: "linkedin" },
  // { name: "Google", icon: "i-bxl-google", slug: "google" },
  // { name: "Apple", icon: "i-bxl-apple", slug: "apple" },
]

// const status: Ref<RequestStatus> = ref("idle")
const login = async (slug: string) => {
  // const authorizationUrl = await myFetch(undefined, status)<string>(`auth/${slug}`)
  // window.location.href = authorizationUrl
}
</script>
