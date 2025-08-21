package com.example.ticket_booking_manager_client.ui

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
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
        val icon: ImageView = v.findViewById(R.id.rowIcon)
        val title: TextView = v.findViewById(R.id.rowTitle)
        val subtitle: TextView = v.findViewById(R.id.rowSubtitle)
        val price: TextView = v.findViewById(R.id.rowPrice)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.row_ticket, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val t = items[position]

        val (iconRes, company) = when {
            !t.airline_name.isNullOrBlank() -> R.drawable.ic_plane_big to t.airline_name
            !t.bus_company.isNullOrBlank()   -> R.drawable.ic_bus_big   to t.bus_company
            !t.train_type.isNullOrBlank()    -> R.drawable.ic_train_big to t.train_type
            else                             -> R.drawable.ic_plane_big to (t.brand ?: "")
        }

        holder.icon.setImageResource(iconRes)
        holder.title.text = "Ticket #${t.ticket_id} • ${company ?: ""}"
        holder.subtitle.text = "${t.departure_time} → ${t.arrival_time}"
        holder.price.text = t.price.toString()
        holder.itemView.setOnClickListener { onClick(t) }
    }

    override fun getItemCount() = items.size
}
