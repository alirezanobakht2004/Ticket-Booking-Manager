package com.example.ticket_booking_manager_client.data

import android.content.Context
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

private val Context.appDataStore by preferencesDataStore("app_prefs")

class AppPrefs(private val context: Context) {
    companion object {
        private val KEY_ONBOARDED = booleanPreferencesKey("onboarded")
    }

    val onboardedFlow = context.appDataStore.data.map { it[KEY_ONBOARDED] ?: false }

    suspend fun setOnboarded(value: Boolean) {
        context.appDataStore.edit { it[KEY_ONBOARDED] = value }
    }

    suspend fun isOnboardedOnce(): Boolean = onboardedFlow.first()
}
