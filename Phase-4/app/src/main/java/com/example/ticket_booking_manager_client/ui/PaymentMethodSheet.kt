package com.example.ticket_booking_manager_client.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import com.example.ticket_booking_manager_client.R
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import com.google.android.material.button.MaterialButton

class PaymentMethodSheet(
    private val onPick: (method: String) -> Unit
) : BottomSheetDialogFragment() {

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        val v = inflater.inflate(R.layout.sheet_payment_method, container, false)
        v.findViewById<MaterialButton>(R.id.btnCard).setOnClickListener {
            onPick("CARD"); dismiss()
        }
        v.findViewById<MaterialButton>(R.id.btnWallet).setOnClickListener {
            onPick("WALLET"); dismiss()
        }
        return v
    }
}
