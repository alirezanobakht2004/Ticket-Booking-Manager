package com.example.ticket_booking_manager_client.data.remote

import com.example.ticket_booking_manager_client.data.remote.models.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    // --- Auth ---
    @POST("api/auth/login/request-otp")
    suspend fun requestOtp(@Body body: OtpRequestBody): Response<ApiMessage>

    @POST("api/auth/login/verify-otp")
    suspend fun verifyOtp(@Body body: VerifyOtpBody): Response<LoginResponse>

    @POST("api/auth/signup")
    suspend fun signup(@Body body: SignupBody): Response<LoginResponse>

    @POST("api/auth/profile/update")
    suspend fun updateProfile(@Body body: UpdateProfileBody): Response<ApiMessage>

    // --- Cities ---
    @GET("api/cities")
    suspend fun getCities(): Response<CitiesResponse>

    // --- Tickets ---
    @GET("api/tickets/search")
    suspend fun searchTickets(
        @Query("origin_id") originId: Int,
        @Query("destination_id") destinationId: Int,
        @Query("travel_date") travelDate: String,
        @Query("vehicle_type") vehicleType: String? = null,
        @Query("min_price") minPrice: Double? = null,
        @Query("max_price") maxPrice: Double? = null,
        @Query("company_name") company: String? = null,
        @Query("departure_start") depStart: String? = null,
        @Query("departure_end") depEnd: String? = null,
        @Query("travel_class") travelClass: Int? = null
    ): Response<TicketsSearchResponse>

    @GET("api/tickets/details/{ticket_id}")
    suspend fun getTicketDetails(@Path("ticket_id") ticketId: Int): Response<TicketDetailsResponse>

    @GET("api/tickets/cancel/check/{ticket_id}")
    suspend fun checkCancelPenalty(@Path("ticket_id") ticketId: Int): Response<CancelPenaltyResponse>

    @POST("api/tickets/cancel/{ticket_id}")
    suspend fun cancelTicket(@Path("ticket_id") ticketId: Int): Response<CancelPerformResponse>

    // --- Reservations ---
    @POST("api/reservations/reserve")
    suspend fun reserveTicket(@Body body: ReserveBody): Response<ReserveResponse>

    @GET("api/reservations/active")
    suspend fun getActiveReservations(): Response<ReservationsResponse>

    @GET("api/reservations/history")
    suspend fun getReservationsHistory(): Response<ReservationsResponse>

    // --- Payments ---
    @POST("api/payments/pay/ticket/{ticket_id}")
    suspend fun payForTicket(
        @Path("ticket_id") ticketId: Int,
        @Body body: PaymentBody
    ): Response<PaymentResponse>

    @POST("api/reservations/pay/{reservation_id}")
    suspend fun payForReservation(
        @Path("reservation_id") reservationId: Int,
        @Body body: PaymentBody
    ): Response<PaymentResponse>
}