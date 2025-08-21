package com.example.ticket_booking_manager_client.data

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore("auth_prefs")

class TokenStore(private val context: Context) {
    companion object {
        private val KEY_JWT = stringPreferencesKey("jwt")
    }

    val tokenFlow = context.dataStore.data.map { it[KEY_JWT] }

    suspend fun saveToken(token: String) {
        context.dataStore.edit { it[KEY_JWT] = token }
    }

    suspend fun clear() {
        context.dataStore.edit { it.remove(KEY_JWT) }
    }

    suspend fun getTokenOnce(): String? = tokenFlow.first()
}
