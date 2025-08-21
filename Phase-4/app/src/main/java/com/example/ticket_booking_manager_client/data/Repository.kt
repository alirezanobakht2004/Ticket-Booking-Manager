package com.example.ticket_booking_manager_client.data

import android.content.Context
import com.example.ticket_booking_manager_client.data.remote.ApiClient
import com.example.ticket_booking_manager_client.data.remote.models.*

class Repository (context: Context) {
    private val api = ApiClient.create(context)

    // Auth
    suspend fun requestOtp(phone: String? = null, email: String? = null) =
        api.requestOtp(OtpRequestBody(phone, email))

    suspend fun verifyOtp(phone: String? = null, email: String? = null, otp: String) =
        api.verifyOtp(VerifyOtpBody(phone, email, otp))

    suspend fun signup(body: SignupBody) = api.signup(body)
    suspend fun updateProfile(body: UpdateProfileBody) = api.updateProfile(body)

    // Cities
    suspend fun getCities() = api.getCities().also {
        android.util.Log.d("APP/Repo", "getCities() called")
    }
    // Tickets
    suspend fun searchTickets(
        originId: Int, destinationId: Int, travelDate: String,
        vehicleType: String? = null, minPrice: Double? = null, maxPrice: Double? = null,
        company: String? = null, depStart: String? = null, depEnd: String? = null,
        travelClass: Int? = null
    ) = api.searchTickets(originId, destinationId, travelDate, vehicleType, minPrice, maxPrice, company, depStart, depEnd, travelClass)

    suspend fun ticketDetails(ticketId: Int) = api.getTicketDetails(ticketId)
    suspend fun checkCancel(ticketId: Int) = api.checkCancelPenalty(ticketId)
    suspend fun cancelTicket(ticketId: Int) = api.cancelTicket(ticketId)

    // Reservations
    suspend fun reserveTicket(ticketId: Int, validity: Int = 10) =
        api.reserveTicket(ReserveBody(ticketId, validity))

    suspend fun activeReservations() = api.getActiveReservations()
    suspend fun reservationsHistory() = api.getReservationsHistory()

    // Payment
    suspend fun payForTicket(ticketId: Int, method: String) =
        api.payForTicket(ticketId, PaymentBody(method))
}
