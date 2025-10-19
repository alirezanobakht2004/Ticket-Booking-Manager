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
    private lateinit var emailEdit: EditText
    private lateinit var phoneEdit: EditText
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
        emailEdit = findViewById(R.id.emailEdit)
        phoneEdit = findViewById(R.id.phoneEdit)
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
                if (resp.isSuccessful) {
                    cities = body?.cities.orEmpty()
                    val names = cities.map { it.title }
                    val adapter = ArrayAdapter(this@RegisterActivity, android.R.layout.simple_spinner_dropdown_item, names)
                    citySpinner.adapter = adapter
                    if (cities.isNotEmpty()) {
                        citySpinner.setSelection(0, false)
                    } else {
                        Toast.makeText(this@RegisterActivity, "No cities returned", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    cities = emptyList()
                    citySpinner.adapter = ArrayAdapter(this@RegisterActivity, android.R.layout.simple_spinner_dropdown_item, emptyList<String>())
                    Toast.makeText(this@RegisterActivity, "Failed cities ${resp.code()}", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                cities = emptyList()
                citySpinner.adapter = ArrayAdapter(this@RegisterActivity, android.R.layout.simple_spinner_dropdown_item, emptyList<String>())
                Toast.makeText(this@RegisterActivity, "Error: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }

        signUpBtn.setOnClickListener { attemptSignup() }
    }

    private fun attemptSignup() {
        val f = firstName.text.toString().trim()
        val l = lastName.text.toString().trim()
        val email = emailEdit.text.toString().trim()
        val phone = phoneEdit.text.toString().trim()
        val pass = password.text.toString()

        if (f.isEmpty()) { toast("Enter first name"); return }
        if (l.isEmpty()) { toast("Enter last name"); return }
        if (email.isEmpty() || !Patterns.EMAIL_ADDRESS.matcher(email).matches()) { toast("Enter a valid email"); return }
        if (phone.isEmpty()) { toast("Enter phone"); return }
        if (pass.length < 6) { toast("Password must be at least 6 characters"); return }

        // Always pick a city: use selected if valid; else default to first if available
        val selectedCity = when {
            cities.isNotEmpty() && citySpinner.selectedItemPosition in cities.indices ->
                cities[citySpinner.selectedItemPosition].title
            cities.isNotEmpty() ->
                cities.first().title
            else ->
                "" // If backend mandates city, you can block submit when cities is empty
        }
        if (selectedCity.isEmpty()) {
            toast("Cities not loaded. Try again.")
            return
        }

        val body = SignupBody(
            first_name = f,
            last_name = l,
            email = email,
            phone_number = normalizePhone(phone),
            city = selectedCity,
            password = pass
        )

        setLoading(true)
        lifecycleScope.launch {
            try {
                val resp = repo.signup(body)
                val code = resp.code()
                val payload = resp.body()
                val msg = payload?.message ?: "Signup failed"

                if (resp.isSuccessful && !payload?.token.isNullOrBlank()) {
                    // Instead of saving token and going to Dashboard,
                    // go to Sign In so the user gets a valid session via OTP verify.
                    Toast.makeText(this@RegisterActivity, getString(R.string.register_success), Toast.LENGTH_SHORT).show()
                    startActivity(Intent(this@RegisterActivity, LoginActivity::class.java).apply {
                        // Optionally prefill email or phone via extras, so login screen can pre-set the field
                        putExtra("prefill_email", email.takeIf { it.isNotBlank() })
                        putExtra("prefill_phone", phone.takeIf { it.isNotBlank() })
                    })
                    finish()
                } else {
                    Toast.makeText(this@RegisterActivity, msg, Toast.LENGTH_SHORT).show()
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

    private fun normalizePhone(input: String): String {
        // Keep leading +; strip spaces, dashes, parentheses
        return input.replace(Regex("[()\\s-]"), "")
    }

    private fun toast(msg: String) = Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
}