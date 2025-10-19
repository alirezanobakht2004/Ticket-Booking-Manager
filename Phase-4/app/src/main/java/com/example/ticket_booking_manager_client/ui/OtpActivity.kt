package com.example.ticket_booking_manager_client.ui

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.ticket_booking_manager_client.R
import com.example.ticket_booking_manager_client.data.Repository
import com.example.ticket_booking_manager_client.data.TokenStore
import kotlinx.coroutines.launch

class OtpActivity : AppCompatActivity() {

    private lateinit var repo: Repository
    private lateinit var tokenStore: TokenStore

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_otp)

        repo = Repository(this)
        tokenStore = TokenStore(this)

        findViewById<com.google.android.material.appbar.MaterialToolbar>(R.id.toolbarBack).apply {
            title = getString(R.string.enter_otp)
            setNavigationOnClickListener { onBackPressedDispatcher.onBackPressed() }
        }

        val otpHint = findViewById<TextView>(R.id.otpHint)
        val otpInput = findViewById<EditText>(R.id.otpInput)
        val submitOtp = findViewById<Button>(R.id.submitOtp)
        val resendOtp = findViewById<Button>(R.id.resendOtp)

        val email = intent.getStringExtra("email")
        val phone = intent.getStringExtra("phone")

        otpHint.text = when {
            !email.isNullOrBlank() -> getString(R.string.otp_sent_to, email)
            !phone.isNullOrBlank() -> getString(R.string.otp_sent_to, phone)
            else -> getString(R.string.otp_sent)
        }

        // Optionally request OTP on entry
        lifecycleScope.launch {
            runCatching {
                when {
                    !email.isNullOrBlank() -> repo.requestOtp(email = email)
                    !phone.isNullOrBlank() -> repo.requestOtp(phone = phone)
                    else -> null
                }
            }.onFailure {
                Toast.makeText(this@OtpActivity, "OTP request error: ${it.message}", Toast.LENGTH_SHORT).show()
            }
        }

        resendOtp.setOnClickListener {
            lifecycleScope.launch {
                runCatching {
                    when {
                        !email.isNullOrBlank() -> repo.requestOtp(email = email)
                        !phone.isNullOrBlank() -> repo.requestOtp(phone = phone)
                        else -> null
                    }
                }.onSuccess {
                    Toast.makeText(this@OtpActivity, getString(R.string.otp_resent), Toast.LENGTH_SHORT).show()
                }.onFailure {
                    Toast.makeText(this@OtpActivity, "Resend failed: ${it.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }

        submitOtp.setOnClickListener {
            val code = otpInput.text.toString().trim()
            if (code.isEmpty()) {
                Toast.makeText(this, getString(R.string.enter_otp), Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            lifecycleScope.launch {
                try {
                    val resp = when {
                        !email.isNullOrBlank() -> repo.verifyOtp(email = email, otp = code)
                        !phone.isNullOrBlank() -> repo.verifyOtp(phone = phone, otp = code)
                        else -> null
                    }
                    if (resp != null && resp.isSuccessful && !resp.body()?.token.isNullOrBlank()) {
                        tokenStore.saveToken(resp.body()!!.token!!)
                        startActivity(Intent(this@OtpActivity, DashboardActivity::class.java).apply {
                            addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK)
                        })
                        finish()
                    } else {
                        Toast.makeText(this@OtpActivity, resp?.body()?.message ?: "OTP verify failed", Toast.LENGTH_SHORT).show()
                    }
                } catch (e: Exception) {
                    Toast.makeText(this@OtpActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}