package com.example.ticket_booking_manager_client.ui

import android.os.Bundle
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.ticket_booking_manager_client.R
import com.example.ticket_booking_manager_client.data.Repository
import com.example.ticket_booking_manager_client.data.remote.models.Reservation
import kotlinx.coroutines.launch

class BookingsActivity : AppCompatActivity() {
    private lateinit var repo: Repository
    private lateinit var activeAdapter: SimpleReservationAdapter
    private lateinit var historyAdapter: SimpleReservationAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_bookings)
        repo = Repository(this)

        val activeRV = findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.activeRV)
        val historyRV = findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.historyRV)

        activeAdapter = SimpleReservationAdapter()
        historyAdapter = SimpleReservationAdapter()

        activeRV.layoutManager = LinearLayoutManager(this)
        activeRV.adapter = activeAdapter
        historyRV.layoutManager = LinearLayoutManager(this)
        historyRV.adapter = historyAdapter

        findViewById<Button>(R.id.refreshActive).setOnClickListener {
            lifecycleScope.launch {
                val resp = repo.activeReservations()
                if (resp.isSuccessful) activeAdapter.submit(resp.body()?.reservations ?: emptyList())
                else Toast.makeText(this@BookingsActivity, "Failed to load active", Toast.LENGTH_SHORT).show()
            }
        }

        findViewById<Button>(R.id.refreshHistory).setOnClickListener {
            lifecycleScope.launch {
                val resp = repo.reservationsHistory()
                if (resp.isSuccessful) historyAdapter.submit(resp.body()?.reservations ?: emptyList())
                else Toast.makeText(this@BookingsActivity, "Failed to load history", Toast.LENGTH_SHORT).show()
            }
        }
    }
}

class SimpleReservationAdapter : androidx.recyclerview.widget.RecyclerView.Adapter<SimpleReservationAdapter.VH>() {
    private var items: List<Reservation> = emptyList()
    fun submit(list: List<Reservation>) { items = list; notifyDataSetChanged() }

    class VH(val v: android.view.View) : androidx.recyclerview.widget.RecyclerView.ViewHolder(v) {
        val t: android.widget.TextView = v.findViewById(android.R.id.text1)
    }

    override fun onCreateViewHolder(p: android.view.ViewGroup, vt: Int): VH {
        val tv = android.widget.TextView(p.context).apply {
            id = android.R.id.text1
            setPadding(12, 12, 12, 12)
            textSize = 14f
        }
        return VH(tv)
    }

    override fun onBindViewHolder(h: VH, pos: Int) {
        val r = items[pos]
        h.t.text = "#${r.reservation_id} • ${r.status} • ${r.reservation_date}"
    }

    override fun getItemCount() = items.size
}
