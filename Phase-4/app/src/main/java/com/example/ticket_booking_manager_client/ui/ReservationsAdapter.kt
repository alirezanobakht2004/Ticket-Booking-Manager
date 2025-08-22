package com.example.ticket_booking_manager_client.ui

import android.os.CountDownTimer
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.core.view.isVisible
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.ticket_booking_manager_client.R
import com.example.ticket_booking_manager_client.data.remote.models.Reservation
import com.google.android.material.button.MaterialButton
import com.google.android.material.chip.Chip
import java.util.Locale
import java.util.concurrent.TimeUnit

// java.time (enable coreLibraryDesugaring if minSdk < 26)
import java.time.Instant
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.time.format.DateTimeParseException
import java.time.temporal.ChronoField

class ReservationsAdapter(
    private val showActions: Boolean,
    private val onAccept: (Reservation) -> Unit,
    private val onReject: (Reservation) -> Unit,
    private val onClick: (Reservation) -> Unit = {}
) : ListAdapter<Reservation, ReservationsAdapter.VH>(Diff) {

    object Diff : DiffUtil.ItemCallback<Reservation>() {
        override fun areItemsTheSame(o: Reservation, n: Reservation) = o.reservation_id == n.reservation_id
        override fun areContentsTheSame(o: Reservation, n: Reservation) = o == n
    }

    class VH(v: View) : RecyclerView.ViewHolder(v) {
        val resId: TextView = v.findViewById(R.id.resId)
        val statusChip: Chip = v.findViewById(R.id.statusChip)
        val countdown: TextView = v.findViewById(R.id.countdown)
        val dateTime: TextView = v.findViewById(R.id.dateTime)
        val acceptBtn: MaterialButton = v.findViewById(R.id.acceptBtn)
        val rejectBtn: MaterialButton = v.findViewById(R.id.rejectBtn)
        val actionsRow: View = v.findViewById(R.id.actionsRow)
        var timer: CountDownTimer? = null
    }

    // ---- Config ----
    private val clockSkewGraceMs = TimeUnit.MINUTES.toMillis(2) // allow 2 minutes grace

    // ---- Formatters ----
    private val isoLocalLenient: DateTimeFormatter by lazy {
        DateTimeFormatterBuilder()
            .appendPattern("yyyy-MM-dd['T'[' ']]HH:mm:ss")
            .optionalStart().appendFraction(ChronoField.NANO_OF_SECOND, 1, 9, true).optionalEnd()
            .toFormatter(Locale.US)
    }
    private val spaceDateTime: DateTimeFormatter by lazy {
        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss", Locale.US)
    }
    private val prettyOut: DateTimeFormatter by lazy {
        DateTimeFormatter.ofPattern("EEE, dd MMM yyyy • HH:mm", Locale.getDefault())
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.row_reservation, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(h: VH, position: Int) {
        h.timer?.cancel()
        val r = getItem(position)

        h.resId.text = "#${r.reservation_id}"

        val status = (r.status ?: "—").uppercase(Locale.US)
        h.statusChip.text = status
        h.statusChip.isClickable = false

        // Prefer reservation_date for display; if missing, show expiry_time; render in LOCAL time
        val pretty = r.reservation_date?.let { prettyLocal(it) }
            ?: r.expiry_time?.let { prettyLocal(it) }
            ?: ""
        h.dateTime.text = pretty

        val actionable = status == "PENDING" || status == "ACTIVE"
        h.actionsRow.isVisible = showActions && actionable

        // Countdown from expiry_time (assumed server UTC)
        val rawLeft = millisUntilUTC(r.expiry_time)
        val msLeft = when {
            rawLeft == Long.MIN_VALUE -> Long.MIN_VALUE // parse failed
            rawLeft >= 0 -> rawLeft
            rawLeft < 0 && -rawLeft <= clockSkewGraceMs -> 0L // within grace: treat as "now"
            else -> rawLeft
        }

        val expired = (msLeft == Long.MIN_VALUE) || (msLeft < 0)

        //h.acceptBtn.isEnabled = !expired && showActions && actionable
        //h.rejectBtn.isEnabled = !expired && showActions && actionable

        h.acceptBtn.setOnClickListener { onAccept(r) }
        h.rejectBtn.setOnClickListener { onReject(r) }

        if (showActions && actionable && msLeft >= 0) {
            h.countdown.isVisible = true
            // If msLeft == 0 (grace), show “expires soon” without a running timer.
            if (msLeft == 0L) {
                h.countdown.text = "expires soon"
            } else {
                h.timer = object : CountDownTimer(msLeft, 1_000) {
                    override fun onTick(millis: Long) {
                        val m = TimeUnit.MILLISECONDS.toMinutes(millis)
                        val s = TimeUnit.MILLISECONDS.toSeconds(millis) % 60
                        h.countdown.text = "expires in %02d:%02d".format(m, s)
                    }
                    override fun onFinish() { h.countdown.text = "expired" }
                }.start()
            }
        } else {
            h.countdown.isVisible = actionable
            h.countdown.text = if (expired) "expired" else ""
        }

        h.itemView.setOnClickListener { onClick(r) }
    }

    override fun onViewRecycled(holder: VH) {
        holder.timer?.cancel()
        holder.timer = null
        super.onViewRecycled(holder)
    }

    // ---------- Helpers ----------

    private fun prettyLocal(s: String): String {
        val inst = parseToInstantAssumingUTC(s) ?: return s
        return prettyOut.format(inst.atZone(ZoneId.systemDefault()))
    }

    private fun millisUntilUTC(s: String?): Long {
        if (s.isNullOrBlank()) return Long.MIN_VALUE
        val target = parseToInstantAssumingUTC(s) ?: return Long.MIN_VALUE
        return target.toEpochMilli() - Instant.now().toEpochMilli()
    }

    /**
     * Parse many possible server shapes into Instant.
     * Supports:
     *  - ISO_INSTANT:               2025-08-22T05:47:35Z
     *  - ISO_OFFSET_DATE_TIME:      2025-08-22T05:47:35+02:00
     *  - RFC_1123_DATE_TIME:        Fri, 22 Aug 2025 05:47:35 GMT
     *  - ISO-like without offset:   2025-08-22T05:47:35[.SSS]  (assume UTC)
     *  - Space-separated:           2025-08-22 05:47:35        (assume UTC)
     */
    private fun parseToInstantAssumingUTC(s: String): Instant? {
        val t = s.trim()
        if (t.isEmpty()) return null

        // Strict ISO instant with Z
        try { return Instant.parse(t) } catch (_: Exception) {}

        // With explicit offset
        try { return OffsetDateTime.parse(t, DateTimeFormatter.ISO_OFFSET_DATE_TIME).toInstant() } catch (_: Exception) {}

        // RFC-1123 (… GMT)
        try { return ZonedDateTime.parse(t, DateTimeFormatter.RFC_1123_DATE_TIME).toInstant() } catch (_: Exception) {}

        // ISO w/o offset (treat as UTC)
        try { return LocalDateTime.parse(t, isoLocalLenient).toInstant(ZoneOffset.UTC) } catch (_: DateTimeParseException) {}

        // Space-separated (treat as UTC)
        try { return LocalDateTime.parse(t, spaceDateTime).toInstant(ZoneOffset.UTC) } catch (_: DateTimeParseException) {}

        return null
    }
}
