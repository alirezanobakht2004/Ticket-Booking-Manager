package com.example.ticket_booking_manager_client.ui

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.ticket_booking_manager_client.R
import com.example.ticket_booking_manager_client.data.Repository
import com.example.ticket_booking_manager_client.data.remote.models.City
import com.example.ticket_booking_manager_client.data.remote.models.TicketListItem
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.datepicker.MaterialDatePicker
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class SearchActivity : AppCompatActivity() {
    private lateinit var repo: Repository
    private lateinit var originSpinner: Spinner
    private lateinit var destinationSpinner: Spinner
    private lateinit var dateEdit: EditText
    private lateinit var vehicleTypeSpinner: Spinner
    private lateinit var minPriceEdit: EditText
    private lateinit var maxPriceEdit: EditText
    private lateinit var companyEdit: EditText
    private lateinit var depStartEdit: EditText
    private lateinit var depEndEdit: EditText
    private lateinit var travelClassEdit: EditText


    private lateinit var resultsRV: androidx.recyclerview.widget.RecyclerView
    private lateinit var adapter: TicketsAdapter
    private lateinit var searchBtn: Button
    private val loading by lazy { findViewById<View>(R.id.searchLoading) }

    private var cities: List<City> = emptyList()

    // Pagination controls (NEW)
    private var page = 1
    private var pageSize = 20
    private lateinit var pageInfo: TextView
    private lateinit var pagePrev: ImageButton
    private lateinit var pageNext: ImageButton

    // Defaults
    private val defaultOriginId = 28
    private val defaultDestinationId = 45
    private val defaultDate = "2025-05-10"
    private val defaultVehicleTypeLabel = "Plane"
    private val defaultMinPrice = "50"
    private val defaultMaxPrice = "500"
    private val defaultCompany = "Flores, Strong and Chase"
    private val defaultDepStart = "08:00"
    private val defaultDepEnd = "20:00"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_search)
        repo = Repository(this)

        originSpinner = findViewById(R.id.originSpinner)
        destinationSpinner = findViewById(R.id.destinationSpinner)
        dateEdit = findViewById(R.id.dateEdit)
        vehicleTypeSpinner = findViewById(R.id.vehicleTypeSpinner)
        minPriceEdit = findViewById(R.id.minPriceEdit)
        maxPriceEdit = findViewById(R.id.maxPriceEdit)
        companyEdit = findViewById(R.id.companyEdit)
        depStartEdit = findViewById(R.id.depStartEdit)
        depEndEdit = findViewById(R.id.depEndEdit)
        travelClassEdit = findViewById(R.id.travelClassEdit)

        // Pagination views (NEW: ensure you add these to layout)
        pageInfo = findViewById(R.id.pageInfo)
        pagePrev = findViewById(R.id.pagePrev)
        pageNext = findViewById(R.id.pageNext)

        resultsRV = findViewById(R.id.resultsRV)
        searchBtn = findViewById(R.id.searchBtn)

        adapter = TicketsAdapter { item ->
            val i = Intent(this, TicketDetailsActivity::class.java)
            i.putExtra("ticket_id", item.ticket_id)
            startActivity(i)
        }
        resultsRV.layoutManager = LinearLayoutManager(this)
        resultsRV.adapter = adapter

        findViewById<MaterialToolbar>(R.id.toolbarBack).apply {
            title = getString(R.string.search_tickets)
            navigationIcon = resources.getDrawable(R.drawable.ic_arrow_back_24, theme)
            setNavigationOnClickListener { onBackPressedDispatcher.onBackPressed() }
        }


        // Prefill defaults
        dateEdit.setText(defaultDate)
        minPriceEdit.setText(defaultMinPrice)
        maxPriceEdit.setText(defaultMaxPrice)
        companyEdit.setText(defaultCompany)
        depStartEdit.setText(defaultDepStart)
        depEndEdit.setText(defaultDepEnd)
        travelClassEdit.setText("")

        val vehicleTypes = listOf("All", "Plane", "Bus", "Train")
        vehicleTypeSpinner.adapter =
            ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, vehicleTypes)
        val vtIndex = vehicleTypes.indexOf(defaultVehicleTypeLabel).takeIf { it >= 0 } ?: 0
        vehicleTypeSpinner.setSelection(vtIndex, false)

        searchBtn.setOnClickListener {
            val dateText = dateEdit.text.toString().trim()
            if (dateText.isEmpty()) openDatePickerThenSearch() else {
                page = 1 // reset pagination on new search (NEW)
                doSearch()
            }
        }

        // Pagination actions (NEW)
        pagePrev.setOnClickListener {
            if (page > 1) {
                page -= 1
                doSearch()
            }
        }
        pageNext.setOnClickListener {
            page += 1
            doSearch()
        }
        updatePageInfo()

        // Load cities
        lifecycleScope.launch {
            android.util.Log.d("APP/SEARCH", "Loading cities for spinners…")
            try {
                val resp = repo.getCities()
                android.util.Log.d("APP/SEARCH", "getCities() -> code=${resp.code()} success=${resp.isSuccessful}")
                if (resp.isSuccessful) {
                    cities = resp.body()?.cities.orEmpty()
                    val names = cities.map { "${it.title} (#${it.location_id})" }
                    val adapterSpinner = ArrayAdapter(this@SearchActivity, android.R.layout.simple_spinner_dropdown_item, names)
                    originSpinner.adapter = adapterSpinner
                    destinationSpinner.adapter = adapterSpinner

                    if (cities.isNotEmpty()) {
                        val originIndex = cities.indexOfFirst { it.location_id == defaultOriginId }.takeIf { it >= 0 } ?: 0
                        val destIndex = cities.indexOfFirst { it.location_id == defaultDestinationId }.takeIf { it >= 0 } ?: (if (cities.size > 1) 1 else 0)
                        originSpinner.setSelection(originIndex, false)
                        destinationSpinner.setSelection(destIndex, false)
                    } else {
                        Toast.makeText(this@SearchActivity, "No cities returned", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    val err = resp.errorBody()?.string()
                    android.util.Log.e("APP/SEARCH", "getCities failed: code=${resp.code()} err=$err")
                    Toast.makeText(this@SearchActivity, "Failed to load cities (${resp.code()})", Toast.LENGTH_LONG).show()
                    cities = emptyList()
                }
            } catch (e: Exception) {
                android.util.Log.e("APP/SEARCH", "getCities exception: ${e.message}", e)
                Toast.makeText(this@SearchActivity, "Error loading cities: ${e.message}", Toast.LENGTH_LONG).show()
                cities = emptyList()
            }
        }

        // Optional: addTextChangedListeners with debounce for companyEdit to call suggest endpoint later.
    }

    private fun openDatePickerThenSearch() {
        val picker = MaterialDatePicker.Builder.datePicker()
            .setTitleText("Select travel date")
            .build()
        picker.addOnPositiveButtonClickListener { utcMillis ->
            val sdf = SimpleDateFormat("yyyy-MM-dd", Locale.US)
            sdf.timeZone = TimeZone.getDefault()
            dateEdit.setText(sdf.format(Date(utcMillis)))
            page = 1 // reset pagination (NEW)
            doSearch()
        }
        picker.show(supportFragmentManager, "date")
    }

    private fun doSearch() {
        if (cities.isEmpty()) {
            Toast.makeText(this, "Cities not loaded yet", Toast.LENGTH_SHORT).show()
            return
        }

        val originIdx = originSpinner.selectedItemPosition.takeIf { it in cities.indices } ?: 0
        val destIdx = destinationSpinner.selectedItemPosition.takeIf { it in cities.indices } ?: if (cities.size > 1) 1 else 0
        if (originIdx == destIdx) {
            Toast.makeText(this, "Origin and destination cannot be the same", Toast.LENGTH_SHORT).show()
            return
        }

        val originId = cities[originIdx].location_id
        val destId = cities[destIdx].location_id
        val date = dateEdit.text.toString().trim()

        val vehicleTypeLabel = vehicleTypeSpinner.selectedItem?.toString()?.trim()
        // Normalize to backend expectations (lowercase or null)
        val vehicleType = when (vehicleTypeLabel) {
            "Plane" -> "plane"
            "Bus" -> "bus"
            "Train" -> "train"
            else -> null
        }

        val minPrice = minPriceEdit.text.toString().trim().takeIf { it.isNotEmpty() }?.toDoubleOrNull()
        val maxPrice = maxPriceEdit.text.toString().trim().takeIf { it.isNotEmpty() }?.toDoubleOrNull()
        val company = companyEdit.text.toString().trim().takeIf { it.isNotEmpty() }

        val depStart = depStartEdit.text.toString().trim().takeIf { it.matches(Regex("\\d{2}:\\d{2}")) }
        val depEnd = depEndEdit.text.toString().trim().takeIf { it.matches(Regex("\\d{2}:\\d{2}")) }
        val travelClass = travelClassEdit.text.toString().trim().takeIf { it.isNotEmpty() }?.toIntOrNull()

        android.util.Log.d(
            "APP/SEARCH",
            "doSearch originId=$originId destId=$destId date=$date vehicle=$vehicleType min=$minPrice max=$maxPrice company=$company depStart=$depStart depEnd=$depEnd class=$travelClass page=$page size=$pageSize"
        )

        setLoading(true)
        lifecycleScope.launch {
            try {
                val resp = repo.searchTickets(
                    originId = originId,
                    destinationId = destId,
                    travelDate = date,
                    vehicleType = vehicleType,
                    minPrice = minPrice,
                    maxPrice = maxPrice,
                    company = company,
                    depStart = depStart,
                    depEnd = depEnd,
                    travelClass = travelClass,
                    page = page,
                    pageSize = pageSize
                )
                android.util.Log.d("APP/SEARCH", "searchTickets -> code=${resp.code()} success=${resp.isSuccessful}")
                if (resp.isSuccessful) {
                    val list: List<TicketListItem> = resp.body()?.tickets.orEmpty()
                    adapter.submitList(list)
                    if (list.isEmpty() && page > 1) {
                        Toast.makeText(this@SearchActivity, "No more results", Toast.LENGTH_SHORT).show()
                        if (page > 1) page -= 1
                    }
                } else {
                    val err = resp.errorBody()?.string()
                    android.util.Log.e("APP/SEARCH", "searchTickets failed code=${resp.code()} err=$err")
                    Toast.makeText(this@SearchActivity, "Search failed: ${resp.code()}", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                android.util.Log.e("APP/SEARCH", "searchTickets exception: ${e.message}", e)
                Toast.makeText(this@SearchActivity, "Network error: ${e.message}", Toast.LENGTH_LONG).show()
            } finally {
                setLoading(false)
                updatePageInfo()
            }
        }
    }

    private fun updatePageInfo() {
        pageInfo.text = "Page $page"
        pagePrev.isEnabled = page > 1
        pageNext.isEnabled = true // Could be disabled if last page known
    }

    private fun setLoading(loadingNow: Boolean) {
        loading.visibility = if (loadingNow) View.VISIBLE else View.GONE
        searchBtn.isEnabled = !loadingNow
        pagePrev.isEnabled = !loadingNow && page > 1
        pageNext.isEnabled = !loadingNow
    }
}