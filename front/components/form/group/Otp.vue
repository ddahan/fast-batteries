<template>
  <UFormGroup>
    <div class="flex gap-2.5">
      <div v-for="i in Array.from({ length: length }, (_, i) => i)" :key="i" class="w-12">
        <div class="flex gap-1">
          <UInput
            :ref="(el) => (uInputComponents[i] = el)"
            size="xl"
            maxlength="1"
            :type="hide ? 'password' : 'text'"
            :ui="{ base: 'text-center', size: { xl: 'text-lg' } }"
            :autofocus="i === 0 && autoFocus"
            v-model="otp[i]"
            @input="autoTab(i)"
            @focus="selectTextOnFocus(i)"
            @paste="handlePaste($event)"
            @keydown.delete="handleBackspace(i, $event)"
          />
        </div>
      </div>
    </div>
  </UFormGroup>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    length?: number;
    autoFocus?: boolean;
    autoValidation?: boolean; // only applied on pasting for better UX
    hide?: boolean;
  }>(),
  { length: 6, autoFocus: true, autoValidation: true, hide: false }
);

const emit = defineEmits(["update:modelValue", "otpAutoSubmit"]);

// State
const otp: Ref<string[]> = ref(Array(props.length).fill(""));
const uInputComponents: Ref<any[]> = ref(Array(props.length).fill(null));

// Send code string to the parent component
const code: Ref<string> = computed(() => Object.values(otp.value).join(""));
watch(code, (newCode) => {
  emit("update:modelValue", newCode);
});

const autoTab = async (i: number) => {
  /* auto-focus next input after typing */

  await nextTick(); // wait until Vue completes the DOM updates.
  if (i < props.length - 1 && otp.value[i]) {
    const nextInput = uInputComponents.value[i + 1].input;
    if (nextInput) {
      nextInput.focus();
    }
  }
};

const selectTextOnFocus = (i: number) => {
  /* auto-select input content when focusing it */

  const input = uInputComponents.value[i].input;
  input.select();
};

const handlePaste = async (event: ClipboardEvent) => {
  /* handle the case where the user paste the code (+ auto validation) */

  event.preventDefault();
  const pastedText = event.clipboardData?.getData("text").trim();
  // Paste is disabled if the text is not the right size
  if (pastedText?.length === props.length) {
    otp.value = [...pastedText].map((char, i) => char || "");
    uInputComponents.value[props.length - 1].input.focus();

    const allFieldsFilled = otp.value.every((x) => x.length === 1);
    if (allFieldsFilled && props.autoValidation) {
      await nextTick(); // prevent otpAutoSubmit to be called before code update
      emit("otpAutoSubmit");
    }
  }
};

const handleBackspace = async (i: number, event: KeyboardEvent) => {
  /* Inteligent erasing that goes to previous field after deletion */

  event.preventDefault(); // avoid a race condition with the focus below
  otp.value[i] = ""; // deletion
  if (i > 0) {
    uInputComponents.value[i - 1].input.focus();
  }
};
</script>
