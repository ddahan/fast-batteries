import type { Config } from "tailwindcss"
import colors from "tailwindcss/colors"

export default <Partial<Config>>{
  content: ["./nuxt.config.{js,ts}"],
  theme: {
    extend: {
      colors: {
        right: colors.emerald,
        warn: colors.amber,
        wrong: colors.red,
      },
    },
  },
  future: {
    // https://github.com/tailwindlabs/tailwindcss/discussions/1739
    hoverOnlyWhenSupported: true,
  },
}
