package com.example.ticket_booking_manager_client.ui

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.core.splashscreen.SplashScreen
import androidx.lifecycle.lifecycleScope
import com.example.ticket_booking_manager_client.MainActivity
import com.example.ticket_booking_manager_client.data.AppPrefs
import kotlinx.coroutines.launch
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
class SplashActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
// Call the extension on the Activity, not on SplashScreen
        val splash = installSplashScreen()
        super.onCreate(savedInstanceState)
        val prefs = AppPrefs(this)
        lifecycleScope.launch {
            val seen = prefs.isOnboardedOnce()
            if (seen) {
                startActivity(Intent(this@SplashActivity, MainActivity::class.java))
            } else {
                startActivity(Intent(this@SplashActivity, OnboardingActivity::class.java))
            }
            finish()
        }
    }
}