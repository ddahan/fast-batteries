export const myFetch = (form?: Ref, status = ref("idle")) => {
  const { backHostUrl, apiBase } = useRuntimeConfig().public
  const { hasToken, getToken } = useAuthService()
  status.value = "pending"

  return $fetch.create({
    baseURL: `${backHostUrl}/${apiBase}`,
    timeout: 5000,
    onRequest({ options }) {
      if (hasToken()) {
        // pass the header systematically if it's available
        options.headers.set("Authorization", `Bearer ${getToken()}`)
      }
    },
    // Called when the request can not be executed at all
    async onRequestError({ request, error }) {
      status.value = "error"
      if (error.name === "TypeError") {
        addErrorToast(
          "Error",
          "The server is unavailable. Please try again later or contact support if the issue persists."
        )
      }

      if (error.name === "AbortError" || error.name === "TimeoutError") {
        addErrorToast(
          "Error",
          "The request has timed out, indicating the server may be unavailable. Please try again later or contact support if the issue persists."
        )
      }
    },
    onResponse({ response }) {
      status.value = response.ok ? "success" : "error"
    },
    // Called when the request is executed correctly but the server returns an error
    // Handle display of the error payload, which can contains multiple error messages
    async onResponseError({ response }) {
      const errorPayload: ErrorPayload = response._data.errors

      // -- Display a toast for each general error
      errorPayload.general?.forEach((message) => {
        addErrorToast("Error", message)
      })

      // -- Add a 'nonfield' for each non field error
      errorPayload.nonfield?.forEach((message) => {
        form!.value.setErrors([{ name: "nonfield", message: message }])
      })

      // -- Add a field error for each field error
      Object.entries(errorPayload.field || {}).forEach(([key, message]) => {
        form!.value.setErrors([{ name: key, message: message }])
      })

      if (response.status === 401 || response.status === 403) {
        // could we logout? Or it would be too agressive?
      }
    },
  })
}
