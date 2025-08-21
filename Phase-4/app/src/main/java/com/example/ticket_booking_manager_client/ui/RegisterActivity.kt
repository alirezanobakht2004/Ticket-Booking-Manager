package com.example.ticket_booking_manager_client.ui

import android.content.Intent
import android.os.Bundle
import android.util.Patterns
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.ticket_booking_manager_client.R
import com.example.ticket_booking_manager_client.data.Repository
import com.example.ticket_booking_manager_client.data.TokenStore
import com.example.ticket_booking_manager_client.data.remote.models.City
import com.example.ticket_booking_manager_client.data.remote.models.SignupBody
import kotlinx.coroutines.launch

class RegisterActivity : AppCompatActivity() {


    private lateinit var repo: Repository
    private lateinit var tokenStore: TokenStore

    private lateinit var firstName: EditText
    private lateinit var lastName: EditText
    private lateinit var phoneOrEmail: EditText
    private lateinit var password: EditText
    private lateinit var citySpinner: Spinner
    private lateinit var signUpBtn: com.google.android.material.button.MaterialButton
    private lateinit var progress: View

    private var cities: List<City> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_register)

        repo = Repository(this)
        tokenStore = TokenStore(this)

        findViewById<com.google.android.material.appbar.MaterialToolbar>(R.id.toolbarBack).apply {
            title = getString(R.string.register)
            navigationIcon = resources.getDrawable(R.drawable.ic_arrow_back_24, theme)
            setNavigationOnClickListener { onBackPressedDispatcher.onBackPressed() }
        }

        firstName = findViewById(R.id.firstName)
        lastName = findViewById(R.id.lastName)
        phoneOrEmail = findViewById(R.id.phoneOrEmail)
        password = findViewById(R.id.password)
        citySpinner = findViewById(R.id.citySpinner)
        signUpBtn = findViewById(R.id.signUpBtn)
        progress = findViewById(R.id.signupLoading)

        lifecycleScope.launch {
            android.util.Log.d("APP/REG", "Loading cities…")
            try {
                val resp = repo.getCities()
                android.util.Log.d("APP/REG", "Response: code=${resp.code()} success=${resp.isSuccessful}")
                val body = resp.body()
                if (body == null) {
                    android.util.Log.e("APP/REG", "Body is null")
                    Toast.makeText(this@RegisterActivity, "Cities body null", Toast.LENGTH_SHORT).show()
                } else {
                    android.util.Log.d("APP/REG", "Body status=${body.status} cities.size=${body.cities.size}")
                }

                if (resp.isSuccessful) {
                    val list = body?.cities.orEmpty()
                    cities = list
                    val names = list.map { it.title }
                    android.util.Log.d("APP/REG", "Parsed cities: ${names.size} -> ${names.take(5)}…")
                    val adapter = ArrayAdapter(this@RegisterActivity, android.R.layout.simple_spinner_dropdown_item, names)
                    citySpinner.adapter = adapter
                    if (names.isEmpty()) {
                        Toast.makeText(this@RegisterActivity, "No cities returned", Toast.LENGTH_SHORT).show()
                    } else {
                        citySpinner.setSelection(0, false)
                        android.util.Log.d("APP/REG", "Spinner set with ${names.size} items, first=${names}")
                    }
                } else {
                    val err = resp.errorBody()?.string()
                    android.util.Log.e("APP/REG", "Failed: code=${resp.code()} error=$err")
                    Toast.makeText(this@RegisterActivity, "Failed cities ${resp.code()}", Toast.LENGTH_LONG).show()
                    cities = emptyList()
                    citySpinner.adapter = ArrayAdapter(this@RegisterActivity, android.R.layout.simple_spinner_dropdown_item, emptyList<String>())
                }
            } catch (e: Exception) {
                android.util.Log.e("APP/REG", "Exception loading cities", e)
                Toast.makeText(this@RegisterActivity, "Error: ${e.message}", Toast.LENGTH_LONG).show()
                cities = emptyList()
                citySpinner.adapter = ArrayAdapter(this@RegisterActivity, android.R.layout.simple_spinner_dropdown_item, emptyList<String>())
            }
        }

        signUpBtn.setOnClickListener { attemptSignup() }
    }

    private fun attemptSignup() {
        val f = firstName.text.toString().trim()
        val l = lastName.text.toString().trim()
        val contact = phoneOrEmail.text.toString().trim()
        val pass = password.text.toString()

        if (f.isEmpty()) { toast("Enter first name"); return }
        if (l.isEmpty()) { toast("Enter last name"); return }
        if (contact.isEmpty()) { toast("Enter phone or email"); return }
        if (pass.length < 6) { toast("Password must be at least 6 characters"); return }

        val email = if (isEmail(contact)) contact else ""
        val phone = if (!isEmail(contact)) normalizePhone(contact) else ""

        if (email.isEmpty() && phone.isEmpty()) {
            toast("Enter a valid email or phone")
            return
        }

        val selectedCity = if (cities.isNotEmpty() && citySpinner.selectedItemPosition >= 0)
            cities[citySpinner.selectedItemPosition].title
        else
            ""

        val body = SignupBody(
            first_name = f,
            last_name = l,
            email = email,
            phone_number = phone,
            city = selectedCity,
            password = pass
        )

        setLoading(true)
        lifecycleScope.launch {
            try {
                val resp = repo.signup(body)
                if (resp.isSuccessful && !resp.body()?.token.isNullOrBlank()) {
                    tokenStore.saveToken(resp.body()!!.token!!)
                    toast(getString(R.string.register_success))
                    val i = Intent(this@RegisterActivity, DashboardActivity::class.java)
                    i.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK)
                    startActivity(i)
                    finish()
                } else {
                    // Signup failed (e.g., 409 existing user). Follow backend flow:
                    // 1) Request OTP to the same contact
                    runCatching {
                        when {
                            email.isNotBlank() -> repo.requestOtp(email = email)
                            phone.isNotBlank() -> repo.requestOtp(phone = phone)
                            else -> null
                        }
                    }
                    // 2) Navigate to OTP page to verify and get JWT
                    startActivity(Intent(this@RegisterActivity, OtpActivity::class.java).apply {
                        putExtra("email", email.takeIf { it.isNotBlank() })
                        putExtra("phone", phone.takeIf { it.isNotBlank() })
                    })
                    Toast.makeText(this@RegisterActivity, resp.body()?.message ?: "Proceed with OTP to complete", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                toast("Error: ${e.message}")
            } finally {
                setLoading(false)
            }
        }
    }

    private fun setLoading(loading: Boolean) {
        signUpBtn.isEnabled = !loading
        progress.visibility = if (loading) View.VISIBLE else View.GONE
    }

    private fun isEmail(input: String): Boolean {
        return input.contains("@") && Patterns.EMAIL_ADDRESS.matcher(input).matches()
    }

    private fun normalizePhone(input: String): String {
        return input.replace(Regex("[()\\s-]"), "")
    }

    private fun toast(msg: String) = Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
}