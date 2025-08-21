package com.example.ticket_booking_manager_client.ui

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
            setNavigationOnClickListener { onBackPressedDispatcher.onBackPressed() }
        }

        firstName = findViewById(R.id.firstName)
        lastName = findViewById(R.id.lastName)
        phoneOrEmail = findViewById(R.id.phoneOrEmail)
        password = findViewById(R.id.password)
        citySpinner = findViewById(R.id.citySpinner)
        signUpBtn = findViewById(R.id.signUpBtn)
        progress = findViewById(R.id.signupLoading)

        // Load cities for a friendly dropdown (optional)
        lifecycleScope.launch {
            runCatching { repo.getCities() }
                .onSuccess { resp ->
                    cities = resp.body()?.cities.orEmpty()
                    val names = cities.map { it.title }
                    val adapter = ArrayAdapter(this@RegisterActivity, android.R.layout.simple_spinner_dropdown_item, names)
                    citySpinner.adapter = adapter
                }
        }

        signUpBtn.setOnClickListener {
            attemptSignup()
        }
    }

    private fun attemptSignup() {
        val f = firstName.text.toString().trim()
        val l = lastName.text.toString().trim()
        val contact = phoneOrEmail.text.toString().trim()
        val pass = password.text.toString()

        // Basic validations
        if (f.isEmpty()) { toast("Enter first name"); return }
        if (l.isEmpty()) { toast("Enter last name"); return }
        if (contact.isEmpty()) { toast("Enter phone or email"); return }
        if (pass.length < 6) { toast("Password must be at least 6 characters"); return }

        val isEmail = contact.contains("@") && Patterns.EMAIL_ADDRESS.matcher(contact).matches()
        val isPhone = contact.any { it.isDigit() } && !contact.contains("@")

        if (!isEmail && !isPhone) {
            toast("Enter a valid email or phone")
            return
        }

        val selectedCity = if (cities.isNotEmpty() && citySpinner.selectedItemPosition >= 0)
            cities[citySpinner.selectedItemPosition].title
        else
            "" // allow empty if not required; or enforce selection

        val body = SignupBody(
            first_name = f,
            last_name = l,
            email = if (isEmail) contact else "",
            phone_number = if (isPhone) contact else "",
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
                    finish() // go back, MainActivity will see token and update
                } else {
                    toast(resp.body()?.message ?: "Signup failed")
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

    private fun toast(msg: String) = Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
}