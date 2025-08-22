package com.example.ticket_booking_manager_client.ui

import android.content.Context
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.util.Patterns
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.content.res.AppCompatResources
import androidx.lifecycle.lifecycleScope
import com.example.ticket_booking_manager_client.R
import com.example.ticket_booking_manager_client.data.Repository
import com.example.ticket_booking_manager_client.data.TokenStore
import com.example.ticket_booking_manager_client.data.remote.models.CitiesResponse
import com.example.ticket_booking_manager_client.data.remote.models.UpdateProfileBody
import com.example.ticket_booking_manager_client.util.JwtUtils
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.snackbar.Snackbar
import com.google.android.material.textfield.MaterialAutoCompleteTextView
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class ProfileActivity : AppCompatActivity() {

    private lateinit var repo: Repository
    private lateinit var tokenStore: TokenStore

    private lateinit var firstNameInput: TextInputEditText
    private lateinit var lastNameInput: TextInputEditText
    private lateinit var emailInput: TextInputEditText
    private lateinit var phoneInput: TextInputEditText
    private lateinit var cityInput: MaterialAutoCompleteTextView
    private lateinit var progress: View

    private lateinit var toolbar: MaterialToolbar
    private lateinit var saveBtn: View
    private lateinit var logoutBtn: View

    // For change detection (original values)
    private var origFirst = ""
    private var origLast = ""
    private var origEmail = ""
    private var origPhone = ""
    private var origCity  = ""

    private val textWatcher = object : TextWatcher {
        override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
        override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) { refreshSaveEnabled() }
        override fun afterTextChanged(s: Editable?) {}
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)

        repo = Repository(this)
        tokenStore = TokenStore(this)

        toolbar = findViewById(R.id.toolbar)
        toolbar.navigationIcon = AppCompatResources.getDrawable(this, R.drawable.ic_arrow_back_24)
        toolbar.setNavigationOnClickListener { onBackPressedDispatcher.onBackPressed() }

        firstNameInput = findViewById(R.id.firstNameInput)
        lastNameInput  = findViewById(R.id.lastNameInput)
        emailInput     = findViewById(R.id.emailInput)
        phoneInput     = findViewById(R.id.phoneInput)
        cityInput      = findViewById(R.id.cityInput)
        progress       = findViewById(R.id.progress)
        saveBtn        = findViewById(R.id.saveBtn)
        logoutBtn      = findViewById(R.id.logoutBtn)

        // Load initial data from local cache + JWT (no hardcoded Intent extras)
        lifecycleScope.launch {
            val prefs = getSharedPreferences("profile", Context.MODE_PRIVATE)

            // Cached first/last/city (what you saved after previous updates)
            origFirst = prefs.getString("first_name", "") ?: ""
            origLast  = prefs.getString("last_name", "") ?: ""
            origCity  = prefs.getString("city", "") ?: ""

            // Email/phone from JWT (authoritative after login)
            val jwt = tokenStore.getTokenOnce()
            origEmail = JwtUtils.claim(jwt, "email") ?: prefs.getString("email", "") ?: ""
            origPhone = JwtUtils.claim(jwt, "phone") ?: prefs.getString("phone_number", "") ?: ""

            // Prefill UI
            firstNameInput.setText(origFirst)
            lastNameInput.setText(origLast)
            emailInput.setText(origEmail)
            phoneInput.setText(origPhone)
            cityInput.setText(origCity)

            // Avatar initials
            val initials = "${origFirst.take(1)}${origLast.take(1)}".uppercase()
            findViewById<android.widget.TextView>(R.id.avatarInitials).text = initials.ifBlank { "🙂" }

            refreshSaveEnabled()
        }

        // Watch fields
        firstNameInput.addTextChangedListener(textWatcher)
        lastNameInput.addTextChangedListener(textWatcher)
        emailInput.addTextChangedListener(textWatcher)
        phoneInput.addTextChangedListener(textWatcher)
        cityInput.addTextChangedListener(textWatcher)

        saveBtn.setOnClickListener { onSave() }
        logoutBtn.setOnClickListener { onLogout() }

        loadCities()
    }

    private fun refreshSaveEnabled() {
        val changed = hasChanges()
        saveBtn.isEnabled = changed && emailIsValid()
    }

    private fun emailIsValid(): Boolean {
        val e = emailInput.text?.toString().orEmpty()
        if (e.isBlank()) return true // allow clearing if server allows
        val valid = Patterns.EMAIL_ADDRESS.matcher(e).matches()
        emailInput.error = if (valid) null else getString(R.string.invalid_email)
        return valid
    }

    private fun hasChanges(): Boolean {
        val f = firstNameInput.text?.toString().orEmpty()
        val l = lastNameInput.text?.toString().orEmpty()
        val e = emailInput.text?.toString().orEmpty()
        val p = phoneInput.text?.toString().orEmpty()
        val c = cityInput.text?.toString().orEmpty()
        return f != origFirst || l != origLast || e != origEmail || p != origPhone || c != origCity
    }

    private fun buildPatch(): UpdateProfileBody {
        val f = firstNameInput.text?.toString().orEmpty()
        val l = lastNameInput.text?.toString().orEmpty()
        val e = emailInput.text?.toString().orEmpty()
        val p = phoneInput.text?.toString().orEmpty()
        val c = cityInput.text?.toString().orEmpty()

        return UpdateProfileBody(
            first_name   = f.takeIf { it != origFirst && it.isNotBlank() },
            last_name    = l.takeIf { it != origLast && it.isNotBlank() },
            email        = e.takeIf { it != origEmail && it.isNotBlank() },
            phone_number = p.takeIf { it != origPhone && it.isNotBlank() },
            city         = c.takeIf { it != origCity && it.isNotBlank() }
        )
    }

    private fun onSave() {
        if (!hasChanges()) {
            Snackbar.make(saveBtn, getString(R.string.nothing_to_update), Snackbar.LENGTH_SHORT).show()
            return
        }
        if (!emailIsValid()) return

        val patch = buildPatch()
        if (patch.first_name == null &&
            patch.last_name == null &&
            patch.email == null &&
            patch.phone_number == null &&
            patch.city == null
        ) {
            Snackbar.make(saveBtn, getString(R.string.nothing_to_update), Snackbar.LENGTH_SHORT).show()
            return
        }

        setBusy(true)
        lifecycleScope.launch {
            try {
                val resp = repo.updateProfile(patch)
                if (resp.isSuccessful) {
                    // Update originals
                    patch.first_name?.let { origFirst = it }
                    patch.last_name?.let { origLast = it }
                    patch.email?.let { origEmail = it }
                    patch.phone_number?.let { origPhone = it }
                    patch.city?.let { origCity = it }

                    // Persist to a small local cache so next open shows updated values
                    val prefs = getSharedPreferences("profile", Context.MODE_PRIVATE)
                    prefs.edit().apply {
                        patch.first_name?.let { putString("first_name", it) }
                        patch.last_name?.let { putString("last_name", it) }
                        patch.email?.let { putString("email", it) }
                        patch.phone_number?.let { putString("phone_number", it) }
                        patch.city?.let { putString("city", it) }
                    }.apply()

                    Snackbar.make(saveBtn, getString(R.string.profile_updated), Snackbar.LENGTH_LONG).show()
                    refreshSaveEnabled()
                } else {
                    val msg = resp.errorBody()?.string().orEmpty().ifBlank { resp.message() }
                    Toast.makeText(this@ProfileActivity, msg, Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@ProfileActivity, e.message ?: "Update failed", Toast.LENGTH_LONG).show()
            } finally {
                setBusy(false)
            }
        }
    }

    private fun loadCities() {
        lifecycleScope.launch {
            try {
                val resp = repo.getCities()
                if (resp.isSuccessful) {
                    val data: CitiesResponse? = resp.body()
                    val names = (data?.cities ?: emptyList()).map { it.title }
                    withContext(Dispatchers.Main) {
                        cityInput.setAdapter(
                            ArrayAdapter(this@ProfileActivity, android.R.layout.simple_list_item_1, names)
                        )
                    }
                } else {
                    Snackbar.make(cityInput, getString(R.string.cities_load_failed), Snackbar.LENGTH_SHORT).show()
                }
            } catch (_: Exception) {
                Snackbar.make(cityInput, getString(R.string.cities_load_failed), Snackbar.LENGTH_SHORT).show()
            }
        }
    }

    private fun setBusy(busy: Boolean) {
        progress.visibility = if (busy) View.VISIBLE else View.GONE
        saveBtn.isEnabled = !busy && hasChanges() && emailIsValid()
    }

    private fun onLogout() {
        // Clear token + cached profile if desired
        lifecycleScope.launch {
            try {
                tokenStore.clear()
            } catch (_: Exception) {}
            getSharedPreferences("profile", Context.MODE_PRIVATE).edit().clear().apply()
            setResult(RESULT_OK)
            finish()
        }
    }
}
