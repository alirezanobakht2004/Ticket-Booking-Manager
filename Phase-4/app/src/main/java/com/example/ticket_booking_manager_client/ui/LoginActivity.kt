package com.example.ticket_booking_manager_client.ui

import android.content.Intent
import android.os.Bundle
import android.util.Patterns
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
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

        findViewById<com.google.android.material.appbar.MaterialToolbar>(R.id.toolbarBack).apply {
            title = getString(R.string.login)
            navigationIcon = resources.getDrawable(R.drawable.ic_arrow_back_24, theme)
            setNavigationOnClickListener { onBackPressedDispatcher.onBackPressed() }
        }

        val goToRegister = findViewById<com.google.android.material.button.MaterialButton>(R.id.goToRegister)
        goToRegister.setOnClickListener {
            startActivity(Intent(this, RegisterActivity::class.java))
        }

        requestOtp.setOnClickListener {
            val input = phoneOrEmail.text.toString().trim()
            if (input.isEmpty()) {
                Toast.makeText(this, "Enter phone or email", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            requestOtp.isEnabled = false
            lifecycleScope.launch {
                try {
                    val resp = if (isEmail(input)) repo.requestOtp(email = input) else repo.requestOtp(phone = normalizePhone(input))
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
            if (input.isEmpty()) {
                Toast.makeText(this, "Enter phone or email", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (otp.isEmpty()) {
                Toast.makeText(this, "Enter OTP", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            verifyOtp.isEnabled = false
            lifecycleScope.launch {
                try {
                    val resp = if (isEmail(input)) {
                        repo.verifyOtp(email = input, otp = otp)
                    } else {
                        repo.verifyOtp(phone = normalizePhone(input), otp = otp)
                    }
                    if (resp.isSuccessful && !resp.body()?.token.isNullOrBlank()) {
                        tokenStore.saveToken(resp.body()!!.token!!)
                        val i = Intent(this@LoginActivity, DashboardActivity::class.java)
                        i.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK)
                        startActivity(i)
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

    private fun isEmail(input: String): Boolean {
        return input.contains("@") && Patterns.EMAIL_ADDRESS.matcher(input).matches()
    }

    private fun normalizePhone(input: String): String {
        // Only normalize at submit-time (don’t alter what user types)
        return input.replace(Regex("[()\\s-]"), "")
    }
}