package com.example.ticket_booking_manager_client.ui

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.ticket_booking_manager_client.R
import com.example.ticket_booking_manager_client.data.remote.models.TicketListItem
import java.text.NumberFormat
import java.util.Locale

class TicketsAdapter(
    private val onClick: (TicketListItem) -> Unit
) : ListAdapter<TicketListItem, TicketsAdapter.VH>(TicketDiff) {

    private val currency = NumberFormat.getCurrencyInstance(Locale.getDefault())

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
        val t = getItem(position)

        val (iconRes, company) = when {
            !t.airline_name.isNullOrBlank() -> R.drawable.ic_plane_big to t.airline_name
            !t.bus_company.isNullOrBlank()   -> R.drawable.ic_bus_big   to t.bus_company
            !t.train_type.isNullOrBlank()    -> R.drawable.ic_train_big to t.train_type
            else                             -> R.drawable.ic_plane_big to (t.brand ?: "")
        }

        holder.icon.setImageResource(iconRes)
        holder.icon.contentDescription = when (iconRes) {
            R.drawable.ic_bus_big -> "Bus"
            R.drawable.ic_train_big -> "Train"
            else -> "Flight"
        }

        holder.title.text = "Ticket #${t.ticket_id} -  ${company ?: ""}"
        holder.subtitle.text = "${t.departure_time} → ${t.arrival_time}"
        holder.price.text = try {
            currency.format(t.price)
        } catch (_: Exception) {
            t.price.toString()
        }

        holder.itemView.setOnClickListener { onClick(t) }
    }
}

private object TicketDiff : DiffUtil.ItemCallback<TicketListItem>() {
    override fun areItemsTheSame(oldItem: TicketListItem, newItem: TicketListItem) =
        oldItem.ticket_id == newItem.ticket_id

    override fun areContentsTheSame(oldItem: TicketListItem, newItem: TicketListItem) =
        oldItem == newItem
}