package com.example.ticket_booking_manager_client.ui

import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.content.res.AppCompatResources
import androidx.lifecycle.lifecycleScope
import com.example.ticket_booking_manager_client.R
import com.example.ticket_booking_manager_client.data.Repository
import com.google.android.material.appbar.MaterialToolbar
import kotlinx.coroutines.launch
import java.text.NumberFormat
import java.util.Locale

class TicketDetailsActivity : AppCompatActivity() {
    private lateinit var repo: Repository
    private var ticketId: Int = -1

    // Keep the most recent reservation id we create during this session
    private var lastReservationId: Int? = null

    private val detailsText by lazy { findViewById<TextView>(R.id.detailsText) }
    private val reserveBtn by lazy { findViewById<Button>(R.id.reserveBtn) }
    private val payBtn by lazy { findViewById<Button>(R.id.payBtn) }
    private val loading by lazy { findViewById<View>(R.id.detailsLoading) }
    private val currency = NumberFormat.getCurrencyInstance(Locale.getDefault())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_ticket_details)
        repo = Repository(this)
        ticketId = intent.getIntExtra("ticket_id", -1)

        // Back toolbar (Option 1)
        val toolbar = findViewById<MaterialToolbar>(R.id.toolbarBack)
        toolbar.title = getString(R.string.ticket_details)
        toolbar.navigationIcon = AppCompatResources.getDrawable(this, R.drawable.ic_arrow_back_24)
        toolbar.setNavigationOnClickListener { onBackPressedDispatcher.onBackPressed() }

        loadDetails()

        reserveBtn.setOnClickListener { doReserve() }
        payBtn.setOnClickListener { doPay() }
    }

    private fun loadDetails() {
        showLoading(true)
        lifecycleScope.launch {
            try {
                val resp = repo.ticketDetails(ticketId)
                val t = resp.body()?.ticket
                detailsText.text = t?.let {
                    val price = try { currency.format(it.price) } catch (_: Exception) { it.price.toString() }
                    "Ticket #${it.ticket_id}\n${it.origin} → ${it.destination}\n" +
                            "${it.departure_time} → ${it.arrival_time}\nPrice: $price\n" +
                            "Company: ${it.airline_name ?: it.bus_company ?: it.train_type ?: ""}\n" +
                            "Remaining seats: ${it.remaining_capacity ?: "-"}"
                } ?: "No details"
            } catch (e: Exception) {
                Toast.makeText(this@TicketDetailsActivity, "Failed: ${e.message}", Toast.LENGTH_LONG).show()
            } finally {
                showLoading(false)
            }
        }
    }

    private fun doReserve(validityMinutes: Int = 10) {
        setButtonsEnabled(false)
        lifecycleScope.launch {
            try {
                val resp = repo.reserveTicket(ticketId, validityMinutes)
                if (resp.isSuccessful) {
                    val body = resp.body()
                    if (body?.reservation_id != null) {
                        lastReservationId = body.reservation_id
                        Toast.makeText(
                            this@TicketDetailsActivity,
                            "Reserved. ID=$lastReservationId (valid $validityMinutes min)",
                            Toast.LENGTH_SHORT
                        ).show()
                    } else {
                        val msg = "Reserve failed"
                        Toast.makeText(this@TicketDetailsActivity, msg, Toast.LENGTH_SHORT).show()
                    }
                } else {
                    val msg = "Reserve failed (${resp.code()})"
                    Toast.makeText(this@TicketDetailsActivity, msg, Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@TicketDetailsActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
            } finally {
                setButtonsEnabled(true)
            }
        }
    }

    private fun doPay() {
        setButtonsEnabled(false)
        lifecycleScope.launch {
            try {
                if (lastReservationId == null) {
                    val r = repo.reserveTicket(ticketId, 10)
                    if (r.isSuccessful && r.body()?.reservation_id != null) {
                        lastReservationId = r.body()!!.reservation_id
                        Toast.makeText(
                            this@TicketDetailsActivity,
                            "Reserved. ID=$lastReservationId",
                            Toast.LENGTH_SHORT
                        ).show()
                    } else {
                        val msg = "Please reserve first"
                        Toast.makeText(this@TicketDetailsActivity, msg, Toast.LENGTH_SHORT).show()
                        return@launch
                    }
                }

                val resId = lastReservationId!!
                val payResp = repo.payForReservation(resId, "CARD")
                if (payResp.isSuccessful) {
                    val body = payResp.body()
                    if (body?.status == "success") {
                        Toast.makeText(this@TicketDetailsActivity, "Payment successful", Toast.LENGTH_SHORT).show()
                        finish()
                    } else {
                        val msg = body?.message ?: "Payment failed"
                        Toast.makeText(this@TicketDetailsActivity, msg, Toast.LENGTH_SHORT).show()
                    }
                } else {
                    val msg = "Payment failed (${payResp.code()})"
                    Toast.makeText(this@TicketDetailsActivity, msg, Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@TicketDetailsActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
            } finally {
                setButtonsEnabled(true)
            }
        }
    }

    private fun showLoading(show: Boolean) {
        loading.visibility = if (show) View.VISIBLE else View.GONE
    }

    private fun setButtonsEnabled(enabled: Boolean) {
        reserveBtn.isEnabled = enabled
        payBtn.isEnabled = enabled
    }
}