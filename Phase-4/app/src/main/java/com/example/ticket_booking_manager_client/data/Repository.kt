package com.example.ticket_booking_manager_client.data

import android.util.Log
import android.content.Context
import com.example.ticket_booking_manager_client.data.remote.ApiClient
import com.example.ticket_booking_manager_client.data.remote.models.*
import retrofit2.Response

class Repository (context: Context) {
    private val api = ApiClient.create(context)

    // Auth
    suspend fun requestOtp(phone: String? = null, email: String? = null) =
        api.requestOtp(OtpRequestBody(phone, email)).also { resp: Response<ApiMessage> ->
            Log.d("APP/Repo", "requestOtp(phone=${phone?.take(4)}..., email=${email?.take(4)}...) -> code=${resp.code()}")
        }

    suspend fun verifyOtp(phone: String? = null, email: String? = null, otp: String) =
        api.verifyOtp(VerifyOtpBody(phone, email, otp)).also { resp: Response<LoginResponse> ->
            Log.d("APP/Repo", "verifyOtp(phone=${phone?.take(4)}..., email=${email?.take(4)}..., otpLen=${otp.length}) -> code=${resp.code()}")
        }

    suspend fun signup(body: SignupBody) =
        api.signup(body).also { resp: Response<LoginResponse> ->
            Log.d("APP/Repo", "signup(email=${body.email}, phone=${body.phone_number}, city=${body.city}) -> code=${resp.code()}")
        }

    suspend fun updateProfile(body: UpdateProfileBody) =
        api.updateProfile(body).also { resp: Response<ApiMessage> ->
            Log.d("APP/Repo", "updateProfile(...) -> code=${resp.code()}")
        }

    // Cities
    suspend fun getCities() =
        api.getCities().also { resp: Response<CitiesResponse> ->
            Log.d("APP/Repo", "getCities() -> code=${resp.code()}")
        }

    // Tickets
    suspend fun searchTickets(
        originId: Int, destinationId: Int, travelDate: String,
        vehicleType: String? = null, minPrice: Double? = null, maxPrice: Double? = null,
        company: String? = null, depStart: String? = null, depEnd: String? = null,
        travelClass: Int? = null
    ) = api.searchTickets(originId, destinationId, travelDate, vehicleType, minPrice, maxPrice, company, depStart, depEnd, travelClass).also { resp: Response<TicketsSearchResponse> ->
        Log.d("APP/Repo", "searchTickets(origin=$originId, dest=$destinationId, date=$travelDate, vehicle=$vehicleType) -> code=${resp.code()}")
    }

    suspend fun ticketDetails(ticketId: Int) =
        api.getTicketDetails(ticketId).also { resp: Response<TicketDetailsResponse> ->
            Log.d("APP/Repo", "ticketDetails($ticketId) -> code=${resp.code()}")
        }

    suspend fun checkCancel(ticketId: Int) =
        api.checkCancelPenalty(ticketId).also { resp: Response<CancelPenaltyResponse> ->
            Log.d("APP/Repo", "checkCancel($ticketId) -> code=${resp.code()}")
        }

    suspend fun cancelTicket(ticketId: Int) =
        api.cancelTicket(ticketId).also { resp: Response<CancelPerformResponse> ->
            Log.d("APP/Repo", "cancelTicket($ticketId) -> code=${resp.code()}")
        }

    // Reservations
    suspend fun reserveTicket(ticketId: Int, validity: Int = 10) =
        api.reserveTicket(ReserveBody(ticket_id = ticketId, validity_minutes = validity)).also { resp: Response<ReserveResponse> ->
            Log.d("APP/Repo", "reserveTicket(ticket=$ticketId, validity=$validity) -> code=${resp.code()}")
        }

    suspend fun activeReservations() =
        api.getActiveReservations().also { resp: Response<ReservationsResponse> ->
            Log.d("APP/Repo", "activeReservations() -> code=${resp.code()}")
        }

    suspend fun reservationsHistory() =
        api.getReservationsHistory().also { resp: Response<ReservationsResponse> ->
            Log.d("APP/Repo", "reservationsHistory() -> code=${resp.code()}")
        }

    // Payment
    suspend fun payForTicket(ticketId: Int, method: String) =
        api.payForTicket(ticketId, PaymentBody(payment_method = method)).also { resp: Response<PaymentResponse> ->
            Log.d("APP/Repo", "payForTicket(ticket=$ticketId, method=$method) -> code=${resp.code()}")
        }

    // NEW: Pay for a specific reservation_id
    suspend fun payForReservation(reservationId: Int, method: String) =
        api.payForReservation(reservationId, PaymentBody(payment_method = method)).also { resp: Response<PaymentResponse> ->
            Log.d("APP/Repo", "payForReservation(reservation=$reservationId, method=$method) -> code=${resp.code()}")
        }
}