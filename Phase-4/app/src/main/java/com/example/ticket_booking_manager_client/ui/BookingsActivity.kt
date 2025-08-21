package com.example.ticket_booking_manager_client.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.ticket_booking_manager_client.R
import com.example.ticket_booking_manager_client.data.Repository
import com.example.ticket_booking_manager_client.data.remote.models.Reservation
import kotlinx.coroutines.launch

class BookingsActivity : AppCompatActivity() {
    private lateinit var repo: Repository
    private lateinit var activeAdapter: ReservationListAdapter
    private lateinit var historyAdapter: ReservationListAdapter


    private val loadingView by lazy { findViewById<View>(R.id.loadingView) }
    private val emptyView by lazy { findViewById<View>(R.id.emptyView) }
    private val swipe by lazy { findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe) }
    private val activeRV by lazy { findViewById<RecyclerView>(R.id.activeRV) }
    private val historyRV by lazy { findViewById<RecyclerView>(R.id.historyRV) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_bookings)
        repo = Repository(this)

        activeAdapter = ReservationListAdapter()
        historyAdapter = ReservationListAdapter()

        activeRV.layoutManager = LinearLayoutManager(this)
        activeRV.adapter = activeAdapter
        historyRV.layoutManager = LinearLayoutManager(this)
        historyRV.adapter = historyAdapter

        swipe.setOnRefreshListener { loadAll() }

        loadAll()
    }

    private fun loadAll() {
        showLoading(true)
        lifecycleScope.launch {
            try {
                val activeResp = repo.activeReservations()
                val historyResp = repo.reservationsHistory()

                val active = if (activeResp.isSuccessful) activeResp.body()?.reservations.orEmpty() else emptyList()
                val history = if (historyResp.isSuccessful) historyResp.body()?.reservations.orEmpty() else emptyList()

                activeAdapter.submitList(active)
                historyAdapter.submitList(history)
                showEmpty(active.isEmpty() && history.isEmpty())
            } catch (e: Exception) {
                Toast.makeText(this@BookingsActivity, "Failed to load: ${e.message}", Toast.LENGTH_LONG).show()
            } finally {
                showLoading(false)
            }
        }
    }

    private fun showLoading(show: Boolean) {
        loadingView.visibility = if (show) View.VISIBLE else View.GONE
        swipe.isRefreshing = false
    }

    private fun showEmpty(show: Boolean) {
        emptyView.visibility = if (show) View.VISIBLE else View.GONE
    }
}

private object ReservationDiff : DiffUtil.ItemCallback<Reservation>() {
    override fun areItemsTheSame(oldItem: Reservation, newItem: Reservation): Boolean =
        oldItem.reservation_id == newItem.reservation_id


    override fun areContentsTheSame(oldItem: Reservation, newItem: Reservation): Boolean =
        oldItem == newItem
}

private class ReservationListAdapter :
    ListAdapter<Reservation, ReservationListAdapter.VH>(ReservationDiff) {

    class VH(v: View) : RecyclerView.ViewHolder(v) {
        val t: TextView = v.findViewById(android.R.id.text1)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val tv = TextView(parent.context).apply {
            id = android.R.id.text1
            setPadding(24, 24, 24, 24)
            textSize = 15f
        }
        return VH(tv)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val r = getItem(position)
        holder.t.text = "#${r.reservation_id} -  ${r.status ?: "-"} -  ${r.reservation_date ?: "-"}"
    }
}