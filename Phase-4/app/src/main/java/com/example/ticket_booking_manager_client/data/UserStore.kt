package com.example.ticket_booking_manager_client.data

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

private val Context.userData by preferencesDataStore("user_profile")

class UserStore(private val context: Context) {
    companion object {
        private val KEY_FIRST = stringPreferencesKey("first_name")
        private val KEY_LAST  = stringPreferencesKey("last_name")
        private val KEY_EMAIL = stringPreferencesKey("email")
        private val KEY_PHONE = stringPreferencesKey("phone_number")
        private val KEY_CITY  = stringPreferencesKey("city")
    }

    suspend fun save(
        first: String? = null,
        last: String? = null,
        email: String? = null,
        phone: String? = null,
        city: String? = null
    ) {
        context.userData.edit { p ->
            first?.let { p[KEY_FIRST] = it }
            last?.let  { p[KEY_LAST]  = it }
            email?.let { p[KEY_EMAIL] = it }
            phone?.let { p[KEY_PHONE] = it }
            city?.let  { p[KEY_CITY]  = it }
        }
    }

    suspend fun readOnce(): ProfileCache =
        ProfileCache(
            first = context.userData.data.map { it[KEY_FIRST] ?: "" }.first(),
            last  = context.userData.data.map { it[KEY_LAST]  ?: "" }.first(),
            email = context.userData.data.map { it[KEY_EMAIL] ?: "" }.first(),
            phone = context.userData.data.map { it[KEY_PHONE] ?: "" }.first(),
            city  = context.userData.data.map { it[KEY_CITY]  ?: "" }.first(),
        )

    suspend fun clear() { context.userData.edit { it.clear() } }
}

data class ProfileCache(
    val first: String, val last: String,
    val email: String, val phone: String, val city: String
)
