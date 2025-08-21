package com.example.ticket_booking_manager_client.ui

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.ticket_booking_manager_client.R
import com.example.ticket_booking_manager_client.data.remote.models.TicketListItem

class TicketsAdapter(
    private var items: List<TicketListItem>,
    private val onClick: (TicketListItem) -> Unit
) : RecyclerView.Adapter<TicketsAdapter.VH>() {

    fun submit(list: List<TicketListItem>) {
        items = list
        notifyDataSetChanged()
    }

    class VH(v: View) : RecyclerView.ViewHolder(v) {
        val title: TextView = v.findViewById(R.id.rowTitle)
        val subtitle: TextView = v.findViewById(R.id.rowSubtitle)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.row_ticket, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val t = items[position]
        holder.title.text = "Ticket #${t.ticket_id} • ${t.price}"
        holder.subtitle.text = "${t.departure_time} → ${t.arrival_time}  |  ${t.airline_name ?: t.bus_company ?: t.train_type ?: t.brand ?: ""}"
        holder.itemView.setOnClickListener { onClick(t) }
    }

    override fun getItemCount() = items.size
}
