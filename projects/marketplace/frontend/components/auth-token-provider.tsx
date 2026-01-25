"use client"

import { useEffect } from "react"
import { useAuth } from "@clerk/nextjs"

import { setAuthToken } from "@/lib/api"

export default function AuthTokenProvider() {
  const { getToken, isLoaded, userId } = useAuth()

  useEffect(() => {
    let isMounted = true

    const syncToken = async () => {
      if (!isLoaded) {
        return
      }

      if (!userId) {
        setAuthToken(null)
        return
      }

      try {
        const token = await getToken()
        if (isMounted) {
          setAuthToken(token)
        }
      } catch (error) {
        if (isMounted) {
          setAuthToken(null)
        }
      }
    }

    void syncToken()

    return () => {
      isMounted = false
    }
  }, [getToken, isLoaded, userId])

  return null
}
