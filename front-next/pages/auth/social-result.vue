<template>
  <div></div>
</template>

<script setup lang="ts">
// "Chapeau" function to do the right action after an OAuth2 social login is finished
const params = useRoute().query
if ("access_token" in params) {
  login(params)
} else if ("error" in params) {
  addErrorToast("Error", <string>params.error)
  navigateTo("/badges")
} else {
  throw Error("Wrong return response")
}
</script>
