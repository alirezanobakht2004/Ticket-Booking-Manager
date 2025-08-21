package com.example.ticket_booking_manager_client.ui

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.ticket_booking_manager_client.R
import com.example.ticket_booking_manager_client.data.Repository
import kotlinx.coroutines.launch

class TicketDetailsActivity : AppCompatActivity() {
    private lateinit var repo: Repository
    private var ticketId: Int = -1
    private var reserved: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_ticket_details)
        repo = Repository(this)
        ticketId = intent.getIntExtra("ticket_id", -1)

        val detailsText = findViewById<TextView>(R.id.detailsText)
        val reserveBtn = findViewById<Button>(R.id.reserveBtn)
        val payBtn = findViewById<Button>(R.id.payBtn)

        lifecycleScope.launch {
            val resp = repo.ticketDetails(ticketId)
            val t = resp.body()?.ticket
            detailsText.text = t?.let {
                "Ticket #${it.ticket_id}\n${it.origin} → ${it.destination}\n" +
                        "${it.departure_time} → ${it.arrival_time}\nPrice: ${it.price}\n" +
                        "Company: ${it.airline_name ?: it.bus_company ?: it.train_type ?: ""}\n" +
                        "Remaining seats: ${it.remaining_capacity ?: "-"}"
            } ?: "No details"
        }

        reserveBtn.setOnClickListener {
            lifecycleScope.launch {
                val resp = repo.reserveTicket(ticketId, 10)
                if (resp.isSuccessful && resp.body()?.reservation_id != null) {
                    reserved = true
                    Toast.makeText(this@TicketDetailsActivity, "Reserved. ID=${resp.body()!!.reservation_id}", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this@TicketDetailsActivity, "Reserve failed", Toast.LENGTH_SHORT).show()
                }
            }
        }

        payBtn.setOnClickListener {
            lifecycleScope.launch {
                // Payment method string must match backend expectation, e.g., "CARD"
                val resp = repo.payForTicket(ticketId, "CARD")
                if (resp.isSuccessful && resp.body()?.status == "success") {
                    Toast.makeText(this@TicketDetailsActivity, "Payment successful", Toast.LENGTH_SHORT).show()
                    finish()
                } else {
                    Toast.makeText(this@TicketDetailsActivity, resp.body()?.message ?: "Payment failed", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}
