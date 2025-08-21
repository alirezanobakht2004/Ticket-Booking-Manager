package com.example.ticket_booking_manager_client

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.ticket_booking_manager_client.data.TokenStore
import com.example.ticket_booking_manager_client.ui.BookingsActivity
import com.example.ticket_booking_manager_client.ui.LoginActivity
import com.example.ticket_booking_manager_client.ui.SearchActivity
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var tokenStore: TokenStore

    private lateinit var titleTextView: TextView
    private lateinit var authButton: Button
    private lateinit var bookButton: Button
    private lateinit var viewBookingsButton: Button

    private var isLoggedIn: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tokenStore = TokenStore(this)

        titleTextView = findViewById(R.id.titleTextView)
        authButton = findViewById(R.id.authButton)
        bookButton = findViewById(R.id.bookButton)
        viewBookingsButton = findViewById(R.id.viewBookingsButton)

        // Clicks
        authButton.setOnClickListener {
            if (isLoggedIn) {
                lifecycleScope.launch {
                    tokenStore.clear()
                    Toast.makeText(this@MainActivity, "Logged out", Toast.LENGTH_SHORT).show()
                    refreshAuthUi()
                }
            } else {
                startActivity(Intent(this, LoginActivity::class.java))
            }
        }

        bookButton.setOnClickListener {
            if (ensureLoggedIn()) {
                startActivity(Intent(this, SearchActivity::class.java))
            }
        }

        viewBookingsButton.setOnClickListener {
            if (ensureLoggedIn()) {
                startActivity(Intent(this, BookingsActivity::class.java))
            }
        }
    }

    override fun onResume() {
        super.onResume()
        refreshAuthUi()
    }

    private fun ensureLoggedIn(): Boolean {
        return if (isLoggedIn) {
            true
        } else {
            Toast.makeText(this, "Please log in first", Toast.LENGTH_SHORT).show()
            startActivity(Intent(this, LoginActivity::class.java))
            false
        }
    }

    private fun refreshAuthUi() {
        lifecycleScope.launch {
            val token = tokenStore.getTokenOnce()
            isLoggedIn = !token.isNullOrBlank()

            authButton.text = if (isLoggedIn) "Logout" else "Login"
            bookButton.isEnabled = isLoggedIn
            viewBookingsButton.isEnabled = isLoggedIn
        }
    }
}
