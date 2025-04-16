export default defineAppConfig({
  defaultDebounce: 300,
  defaultHide: 1000,
  ui: {
    // theme
    colors: {
      primary: "emerald",
      secondary: "indigo",
      neutral: "slate",
    },
    // components
    button: {
      defaultVariants: {
        size: "lg",
      },
    },
    input: {
      defaultVariants: {
        size: "lg",
      },
    },
    selectMenu: {
      defaultVariants: {
        size: "lg",
      },
    },
  },
})
