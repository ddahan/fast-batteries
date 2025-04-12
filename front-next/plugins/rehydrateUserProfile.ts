export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.hook("app:mounted", async () => {
    const { hasToken } = useAuthService()

    if (hasToken()) {
      try {
        const userData = await myFetch()<UserPublic>("auth/me")
        if (userData) {
          useUserProfile().value = userData
        }
      } catch (error: any) {
        // e.g. token is not valid anymore / user has been deleted from the database
        logout()
      }
    }
  })
})
