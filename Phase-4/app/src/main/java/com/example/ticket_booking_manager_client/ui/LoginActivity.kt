package com.example.ticket_booking_manager_client.ui

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.ticket_booking_manager_client.MainActivity
import com.example.ticket_booking_manager_client.R
import com.example.ticket_booking_manager_client.data.Repository
import com.example.ticket_booking_manager_client.data.TokenStore
import kotlinx.coroutines.launch

class LoginActivity : AppCompatActivity() {
    private lateinit var repo: Repository
    private lateinit var tokenStore: TokenStore

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        repo = Repository(this)
        tokenStore = TokenStore(this)

        val phoneOrEmail = findViewById<EditText>(R.id.phoneOrEmail)
        val requestOtp = findViewById<Button>(R.id.requestOtp)
        val otpInput = findViewById<EditText>(R.id.otpInput)
        val verifyOtp = findViewById<Button>(R.id.verifyOtp)

        requestOtp.setOnClickListener {
            val input = phoneOrEmail.text.toString().trim()
            requestOtp.isEnabled = false
            lifecycleScope.launch {
                try {
                    val resp = if (input.contains("@")) repo.requestOtp(email = input) else repo.requestOtp(phone = input)
                    val msg = resp.body()?.message ?: resp.errorBody()?.string() ?: "OTP requested"
                    Toast.makeText(this@LoginActivity, msg, Toast.LENGTH_SHORT).show()
                } finally {
                    requestOtp.isEnabled = true
                }
            }
        }

        verifyOtp.setOnClickListener {
            val input = phoneOrEmail.text.toString().trim()
            val otp = otpInput.text.toString().trim()
            if (otp.isEmpty()) {
                Toast.makeText(this, "Enter OTP", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            verifyOtp.isEnabled = false
            lifecycleScope.launch {
                try {
                    val resp = if (input.contains("@")) repo.verifyOtp(email = input, otp = otp) else repo.verifyOtp(phone = input, otp = otp)
                    if (resp.isSuccessful && !resp.body()?.token.isNullOrBlank()) {
                        tokenStore.saveToken(resp.body()!!.token!!)
                        startActivity(Intent(this@LoginActivity, com.example.ticket_booking_manager_client.MainActivity::class.java))
                        finish()
                    } else {
                        Toast.makeText(this@LoginActivity, resp.body()?.message ?: "Login failed", Toast.LENGTH_SHORT).show()
                    }
                } finally {
                    verifyOtp.isEnabled = true
                }
            }
        }
    }
}
