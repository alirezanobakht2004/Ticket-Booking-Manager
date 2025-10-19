package com.example.ticket_booking_manager_client.ui

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.example.ticket_booking_manager_client.R
import com.example.ticket_booking_manager_client.ui.BookingsActivity
import com.example.ticket_booking_manager_client.ui.SearchActivity
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.card.MaterialCardView

class DashboardActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        // Top app bar (no back arrow here since it’s the authenticated home)
        findViewById<MaterialToolbar>(R.id.topAppBar).apply {
            title = getString(R.string.dashboard)
        }

        // Action cards
        findViewById<MaterialCardView>(R.id.cardBook).setOnClickListener {
            startActivity(Intent(this, SearchActivity::class.java))
        }

        findViewById<MaterialCardView>(R.id.cardBookings).setOnClickListener {
            startActivity(Intent(this, BookingsActivity::class.java))
        }

        // DashboardActivity.kt
        findViewById<MaterialCardView>(R.id.cardProfile).setOnClickListener {
            startActivity(Intent(this, ProfileActivity::class.java))
        }



        // Add more cards later (profile, settings, support, etc.)
        // findViewById<MaterialCardView>(R.id.cardProfile).setOnClickListener { ... }
    }
}