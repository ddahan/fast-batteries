export const addSuccessToast = (title: string, description?: string) => {
  useToast().add({
    title: title,
    description: description,
    color: "success",
    icon: "i-ph-check-circle-bold",
  })
}

export const addErrorToast = (title: string, description?: string) => {
  useToast().add({
    title: title,
    description: description,
    color: "error",
    icon: "i-ph-x-circle-bold",
  })
}
