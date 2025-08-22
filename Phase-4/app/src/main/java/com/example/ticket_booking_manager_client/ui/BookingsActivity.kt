package com.example.ticket_booking_manager_client.ui

import android.graphics.Rect
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.content.res.AppCompatResources
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.ticket_booking_manager_client.R
import com.example.ticket_booking_manager_client.data.Repository
import com.example.ticket_booking_manager_client.data.remote.models.Reservation
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import kotlinx.coroutines.launch

class BookingsActivity : AppCompatActivity() {

    private lateinit var repo: Repository
    private lateinit var activeAdapter: ReservationsAdapter
    private lateinit var historyAdapter: ReservationsAdapter

    private val loadingView by lazy { findViewById<View>(R.id.loadingView) }
    private val emptyView by lazy { findViewById<View>(R.id.emptyView) }
    private val swipe by lazy { findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe) }
    private val activeRV by lazy { findViewById<RecyclerView>(R.id.activeRV) }
    private val historyRV by lazy { findViewById<RecyclerView>(R.id.historyRV) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_bookings)
        repo = Repository(this)

        // Toolbar with back
        val toolbar = findViewById<MaterialToolbar>(R.id.toolbarBack)
        toolbar.title = getString(R.string.reservations)
        toolbar.navigationIcon = AppCompatResources.getDrawable(this, R.drawable.ic_arrow_back_24)
        toolbar.setNavigationOnClickListener { onBackPressedDispatcher.onBackPressed() }

        // New adapters
        activeAdapter = ReservationsAdapter(
            showActions = true,
            onAccept = { r -> showPaymentSheetAndPay(r) },
            onReject = { r -> confirmLetExpire(r) }
        )
        historyAdapter = ReservationsAdapter(
            showActions = false,
            onAccept = {},
            onReject = {}
        )

        activeRV.layoutManager = LinearLayoutManager(this)
        historyRV.layoutManager = LinearLayoutManager(this)
        activeRV.adapter = activeAdapter
        historyRV.adapter = historyAdapter

        // simple spacing between cards
        val spacing = resources.getDimensionPixelSize(R.dimen.list_item_spacing_8dp)
        val decorator = object : RecyclerView.ItemDecoration() {
            override fun getItemOffsets(outRect: Rect, view: View, parent: RecyclerView, state: RecyclerView.State) {
                outRect.top = spacing
            }
        }
        activeRV.addItemDecoration(decorator)
        historyRV.addItemDecoration(decorator)

        swipe.setOnRefreshListener { loadAll() }
        loadAll()
    }

    private fun showPaymentSheetAndPay(r: Reservation) {
        PaymentMethodSheet { method ->
            payReservation(r, method)
        }.show(supportFragmentManager, "payment_sheet")
    }

    private fun payReservation(r: Reservation, method: String) {
        setLoading(true)
        lifecycleScope.launch {
            try {
                val resp = repo.payReservation(r.reservation_id, method) // POST /api/reservations/pay/{id}
                if (resp.isSuccessful) {
                    toast(getString(R.string.payment_success))
                    loadAll() // refresh; confirmed items will disappear from "active"
                } else {
                    toast(resp.errorBody()?.string() ?: "Payment failed (${resp.code()})")
                }
            } catch (e: Exception) {
                toast("Payment error: ${e.message}")
            } finally {
                setLoading(false)
            }
        }
    }

    private fun confirmLetExpire(r: Reservation) {
        MaterialAlertDialogBuilder(this)
            .setTitle(R.string.let_expire_title)
            .setMessage(R.string.let_expire_msg)
            .setNegativeButton(R.string.cancel, null)
            .setPositiveButton(R.string.let_expire_cta) { _, _ ->
                // UI-only removal (server will naturally expire)
                val newList = activeAdapter.currentList.filter { it.reservation_id != r.reservation_id }
                activeAdapter.submitList(newList)
                showEmpty(newList.isEmpty() && historyAdapter.currentList.isEmpty())
                toast(getString(R.string.let_expire_toast))
            }
            .show()
    }

    private fun loadAll() {
        setLoading(true)
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
                toast("Failed to load: ${e.message}")
            } finally {
                setLoading(false)
                swipe.isRefreshing = false
            }
        }
    }

    private fun setLoading(show: Boolean) {
        loadingView.visibility = if (show) View.VISIBLE else View.GONE
        swipe.isEnabled = !show
    }

    private fun showEmpty(show: Boolean) {
        emptyView.visibility = if (show) View.VISIBLE else View.GONE
    }

    private fun toast(msg: String) =
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
}
