<template>
  <CrudCard v-if="getData">
    <template #header>
      <CrudHeader icon="i-ph-identification-card-bold" title="Badge">
        <template #rightside>
          <ButtonBack />
        </template>
      </CrudHeader>
    </template>

    <!-- Form Content -->
    <FormNonFieldError :form="form" />

    <ContainerVerticalInputs class="mx-auto">
      <FormGroupId :modelValue="getData.id" :inputAttrs="{ class: 'w-full' }" />
      <FormGroupOwner
        v-model="state.owner"
        @update:modelValue="updateData"
        :inputAttrs="{ class: 'w-full' }"
      />
      <FormGroupExpirationDate v-model="state.expireAt" @update:modelValue="updateData" />
      <FormGroupActive v-model="state.isActive" @update:modelValue="updateData" />
    </ContainerVerticalInputs>

    <template #footer>
      <div class="flex items-center justify-between">
        <ButtonConfirmableDelete :status="removeStatus" @confirm="remove" />
        <FormInlineValidator :status="updateStatus" />
      </div>
    </template>
  </CrudCard>
</template>

<script setup lang="ts">
const form = ref()
// NOTE: no need to add a schema as we can't have wrong values here
const badgeUrl = `badges/${useRoute().params.id}`

//////////////////////////////////////////////////////////////////////////////////////////
// Get Badge (for the first time)
//////////////////////////////////////////////////////////////////////////////////////////

const getData = await myFetch()<BadgeOut>(badgeUrl)

const state = reactive({
  owner: getData.owner,
  expireAt: new Date(<string>getData.expireAt),
  isActive: getData.isActive,
})

//////////////////////////////////////////////////////////////////////////////////////////
// Inline Edit Badge
//////////////////////////////////////////////////////////////////////////////////////////

const updateStatus: Ref<RequestStatus> = ref("idle")

const updateData = async () => {
  await myFetch(form, updateStatus)<BadgeOut>(badgeUrl, {
    method: "put",
    body: {
      expireAt: state.expireAt,
      isActive: state.isActive,
      ownerId: state.owner?.id,
    },
  })
}

//////////////////////////////////////////////////////////////////////////////////////////
// Remove Badge
//////////////////////////////////////////////////////////////////////////////////////////

const removeStatus: Ref<RequestStatus> = ref("idle")

const remove = async () => {
  await myFetch(undefined, removeStatus)<{}>(badgeUrl, {
    method: "delete",
  })
  if (removeStatus.value === "success") {
    addSuccessToast("Badge removed")
    await navigateTo(".")
  }
}
</script>
