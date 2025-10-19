package com.example.ticket_booking_manager_client.util

import android.util.Base64
import org.json.JSONObject

object JwtUtils {

    fun payload(token: String?): JSONObject? {
        return try {
            if (token.isNullOrBlank()) return null
            val parts = token.split(".")
            if (parts.size < 2) return null
            val json = String(Base64.decode(parts[1], Base64.URL_SAFE or Base64.NO_WRAP))
            JSONObject(json)
        } catch (_: Exception) {
            null
        }
    }

    fun claim(token: String?, key: String): String? {
        val p = payload(token) ?: return null
        val v = p.optString(key, "")
        return if (v.isNullOrBlank()) null else v
    }
}
