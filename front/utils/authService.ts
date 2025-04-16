const tokenKeyField = "AuthTokenKey"

export const useAuthService = () => {
  const setToken = (newToken: string) => localStorage.setItem(tokenKeyField, newToken)
  const getToken = () => localStorage.getItem(tokenKeyField)
  const hasToken = () => !!getToken()
  const removeToken = () => localStorage.removeItem(tokenKeyField)

  return { setToken, getToken, hasToken, removeToken }
}

// Composable for user profile state
export const useUserProfile = () => useState<UserPublic | undefined>("userProfile", () => undefined)

// Login function that sets the token and fetches the user profile just after
export const login = async (token: Token) => {
  useAuthService().setToken(token.access_token)
  const userData = await myFetch()<UserPublic>("auth/me")

  // Set the user profile
  useUserProfile().value = userData

  // Toast notification and redirect after login
  addSuccessToast("You are connected")
  return navigateTo("/badges")
}

// Logout function that removes the token and redirects the user
export const logout = async (showConfirmMsg = true) => {
  const { hasToken, removeToken } = useAuthService()

  if (hasToken()) {
    removeToken()
  }

  useUserProfile().value = undefined

  if (showConfirmMsg) {
    addSuccessToast("You have been disconnected")
  }

  await navigateTo("/badges")
}
