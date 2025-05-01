// https://stackoverflow.com/a/75926487/2255491
declare function useNuxtApp(): NuxtApp

// Declare backend schema types from generated schemas
import type { components } from "./schemas"

declare global {
  //////////////////////////////////////////////////////////////////////////////////////////////////
  // Meta types
  //////////////////////////////////////////////////////////////////////////////////////////////////
  type Message = components["schemas"]["Message"]
  type ErrorPayload = components["schemas"]["ErrorPayload"]
  type Pagination = components["schemas"]["Pagination"]

  // Generic types are not supported in openAPI, so we need to write the type manually
  interface Page<T> extends Pagination {
    items: T[]
  }

  //////////////////////////////////////////////////////////////////////////////////////////////////
  // Schema types
  //////////////////////////////////////////////////////////////////////////////////////////////////
  type BadgeOut = components["schemas"]["BadgeOut"]
  type BadgeOwner = components["schemas"]["BadgeOwner"]
  type UserPublic = components["schemas"]["UserPublic"]
  type Token = components["schemas"]["Token"]
  type WSChatMessage = components["schemas"]["WSChatMessage"]

  //////////////////////////////////////////////////////////////////////////////////////////////////
  // My custom types
  //////////////////////////////////////////////////////////////////////////////////////////////////
  export type RequestStatus = "idle" | "pending" | "success" | "error"
}

export {} // This is necessary to make the file a module
