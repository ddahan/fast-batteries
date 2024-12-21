export const addSuccessToast = (title: string, description?: string) => {
  useToast().add({
    title: title,
    description: description,
    color: "right",
    icon: "i-ph-check-circle-bold",
  })
}

export const addErrorToast = (title: string, description?: string) => {
  useToast().add({
    title: title,
    description: description,
    color: "wrong",
    icon: "i-ph-x-circle-bold",
  })
}
