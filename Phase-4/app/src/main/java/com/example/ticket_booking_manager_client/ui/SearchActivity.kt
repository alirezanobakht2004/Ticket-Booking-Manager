package com.example.ticket_booking_manager_client.ui

import android.content.Intent
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.ticket_booking_manager_client.R
import com.example.ticket_booking_manager_client.data.Repository
import com.example.ticket_booking_manager_client.data.remote.models.City
import com.example.ticket_booking_manager_client.data.remote.models.TicketListItem
import kotlinx.coroutines.launch

class SearchActivity : AppCompatActivity() {
    private lateinit var repo: Repository
    private lateinit var originSpinner: Spinner
    private lateinit var destinationSpinner: Spinner
    private lateinit var dateEdit: EditText
    private lateinit var resultsRV: androidx.recyclerview.widget.RecyclerView
    private lateinit var adapter: TicketsAdapter
    private var cities: List<City> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_search)
        repo = Repository(this)

        originSpinner = findViewById(R.id.originSpinner)
        destinationSpinner = findViewById(R.id.destinationSpinner)
        dateEdit = findViewById(R.id.dateEdit)
        resultsRV = findViewById(R.id.resultsRV)

        adapter = TicketsAdapter(emptyList()) { item ->
            val i = Intent(this, TicketDetailsActivity::class.java)
            i.putExtra("ticket_id", item.ticket_id)
            startActivity(i)
        }
        resultsRV.layoutManager = LinearLayoutManager(this)
        resultsRV.adapter = adapter

        // at onCreate:
        findViewById<Button>(R.id.searchBtn).setOnClickListener {
            // open MaterialDatePicker if date is empty
            val dateText = dateEdit.text.toString().trim()
            if (dateText.isEmpty()) {
                val picker = com.google.android.material.datepicker.MaterialDatePicker.Builder
                    .datePicker()
                    .setTitleText("Select travel date")
                    .build()
                picker.addOnPositiveButtonClickListener { utcMillis ->
                    val sdf = java.text.SimpleDateFormat("yyyy-MM-dd", java.util.Locale.US)
                    // choose the TZ you want; often user local is nicer than UTC
                    sdf.timeZone = java.util.TimeZone.getDefault()
                    dateEdit.setText(sdf.format(java.util.Date(utcMillis))) // YYYY-MM-DD
                    doSearch()
                }
                picker.show(supportFragmentManager, "date")
            } else {
                doSearch()
            }
        }


        lifecycleScope.launch {
            val resp = repo.getCities()
            cities = resp.body()?.cities ?: emptyList()
            val names = cities.map { "${it.title} (#${it.location_id})" }
            val spinnerAdapter = ArrayAdapter(this@SearchActivity, android.R.layout.simple_spinner_dropdown_item, names)
            originSpinner.adapter = spinnerAdapter
            destinationSpinner.adapter = spinnerAdapter
        }
    }

    private fun doSearch() {
        val originIdx = originSpinner.selectedItemPosition
        val destIdx = destinationSpinner.selectedItemPosition
        if (originIdx < 0 || destIdx < 0) {
            Toast.makeText(this, "Select origin & destination", Toast.LENGTH_SHORT).show()
            return
        }
        val originId = cities[originIdx].location_id
        val destId = cities[destIdx].location_id
        val date = dateEdit.text.toString().trim()
        if (date.isEmpty()) {
            Toast.makeText(this, "Enter date YYYY-MM-DD", Toast.LENGTH_SHORT).show()
            return
        }

        lifecycleScope.launch {
            Toast.makeText(this@SearchActivity, "Searching…", Toast.LENGTH_SHORT).show()
            runCatching { repo.searchTickets(originId, destId, date) }
                .onSuccess { resp ->
                    val list: List<TicketListItem> = resp.body()?.tickets ?: emptyList()
                    adapter.submit(list)
                    if (list.isEmpty()) {
                        Toast.makeText(this@SearchActivity, "No tickets found", Toast.LENGTH_SHORT).show()
                    }
                }
                .onFailure {
                    Toast.makeText(this@SearchActivity, "Network error: ${it.message}", Toast.LENGTH_LONG).show()
                }
        }

    }
}
