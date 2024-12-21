export default defineAppConfig({
  defaultDebounce: 300,
  defaultHide: 1000,
  ui: {
    // theme (Nuxt UI color -> Tailwind color)
    primary: "emerald",
    gray: "slate",
    // theme: custom colors
    right: "right",
    warn: "warn",
    wrong: "wrong",
    // components
    notifications: {
      // Show toasts at the top right of the screen
      position: "bottom-12 left-1/2 transform -translate-x-1/2",
    },
    input: {
      default: {
        size: "lg",
      },
    },
    select: {
      default: {
        size: "lg",
      },
    },
    button: {
      default: {
        size: "lg",
      },
    },
    tooltip: {
      // removes fixed height and truncate
      base: "h-auto overflow-visible text-overflow-clip whitespace-normal",
      popper: { placement: "top" },
    },
  },
})
