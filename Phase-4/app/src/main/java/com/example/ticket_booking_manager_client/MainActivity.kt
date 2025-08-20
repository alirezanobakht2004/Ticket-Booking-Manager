package com.example.ticket_booking_manager_client

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val titleTextView = findViewById<TextView>(R.id.titleTextView)
        val bookButton = findViewById<Button>(R.id.bookButton)
        val viewBookingsButton = findViewById<Button>(R.id.viewBookingsButton)

        bookButton.setOnClickListener {
            Toast.makeText(this, "Book Tickets clicked", Toast.LENGTH_SHORT).show()
            // Add your booking logic here
        }

        viewBookingsButton.setOnClickListener {
            Toast.makeText(this, "View Bookings clicked", Toast.LENGTH_SHORT).show()
            // Add your view bookings logic here
        }
    }
}