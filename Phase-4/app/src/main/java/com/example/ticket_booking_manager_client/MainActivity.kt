package com.example.ticket_booking_manager_client

import android.content.Intent
import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.example.ticket_booking_manager_client.ui.LoginActivity
import com.example.ticket_booking_manager_client.ui.RegisterActivity
import com.google.android.material.button.MaterialButton

class MainActivity : AppCompatActivity() {

    private lateinit var titleTextView: TextView
    private lateinit var signUpButton: MaterialButton
    private lateinit var signInButton: MaterialButton

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        titleTextView = findViewById(R.id.titleTextView)
        signUpButton = findViewById(R.id.signUpButton)
        signInButton = findViewById(R.id.signInButton)

        signUpButton.setOnClickListener {
            startActivity(Intent(this, RegisterActivity::class.java))
        }

        signInButton.setOnClickListener {
            startActivity(Intent(this, LoginActivity::class.java))
        }
    }
}