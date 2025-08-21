package com.example.ticket_booking_manager_client.data.remote.models

// --- common wrapper(s) ---
data class ApiMessage(val status: String?, val message: String?)

// Auth
data class OtpRequestBody(val phone: String? = null, val email: String? = null)
data class VerifyOtpBody(val phone: String? = null, val email: String? = null, val otp: String)
data class SignupBody(
    val first_name: String,
    val last_name: String,
    val email: String,
    val phone_number: String,
    val city: String,
    val password: String
)
data class LoginResponse(val status: String?, val token: String?, val message: String?)

// Profile
data class UpdateProfileBody(
    val first_name: String? = null,
    val last_name: String? = null,
    val phone_number: String? = null,
    val email: String? = null,
    val city: String? = null
)

// Cities
data class CitiesResponse(val status: String?, val cities: List<City> = emptyList())
data class City(val location_id: Int, val title: String)

// Tickets: search result line
data class TicketsSearchResponse(val status: String?, val tickets: List<TicketListItem> = emptyList())
data class TicketListItem(
    val ticket_id: Int,
    val source: Int,
    val destination: Int,
    val departure_time: String,
    val arrival_time: String,
    val price: Double,
    val class_code: Int?,
    val brand: String?,
    val model: String?,
    val bus_company: String?,
    val airline_name: String?,
    val train_type: String?
)

// Ticket details
data class TicketDetailsResponse(val status: String?, val ticket: TicketDetails?)
data class TicketDetails(
    val ticket_id: Int,
    val departure_time: String,
    val arrival_time: String,
    val price: Double,
    val class_code: Int?,
    val origin: String,
    val destination: String,
    val capacity: Int?,
    val reserved_number: Int?,
    val remaining_capacity: Int?,
    val bus_type: String?, val bus_company: String?, val chair_decoration: String?,
    val air_condition: Boolean?, val internet_connection: Boolean?, val snack_service: Boolean?,
    val airline_name: String?, val plane_type: String?, val stops_number: Int?, val flight_number: String?,
    val destination_airport: String?, val departure_airport: String?, val plane_internet_connection: Boolean?,
    val closed_compartment: Boolean?, val bed_chair: Boolean?,
    val train_type: String?, val wagon_count: Int?, val star: Int?, val bus_train: Boolean?,
    val food_service: Boolean?, val train_internet_connection: Boolean?, val train_closed_compartment: Boolean?
)

// Reserve / Reservations
data class ReserveBody(val ticket_id: Int, val validity_minutes: Int = 10)
data class ReserveResponse(val status: String?, val reservation_id: Int?)

data class ReservationsResponse(val status: String?, val reservations: List<Reservation> = emptyList())
data class Reservation(
    val reservation_id: Int,
    val passenger_id: Int?,
    val reservation_date: String?,
    val status: String?,
    val expiry_time: String?
)

// Payments
data class PaymentBody(val payment_method: String) // e.g. "CARD"
data class PaymentResponse(
    val status: String?,
    val message: String?,
    val ticket_details: List<IssuedTicket>?
)
data class IssuedTicket(
    val ticket_id: Int,
    val vehicle_id: Int?,
    val price: Double,
    val departure_time: String,
    val arrival_time: String
)

// Cancellation
data class CancelPenaltyResponse(
    val status: String?,
    val ticket_id: Int?,
    val ticket_price: Double?,
    val departure_time: String?,
    val hours_remaining: Double?,
    val penalty_percentage: Int?,
    val penalty_amount: Double?,
    val refundable_amount: Double?
)

data class CancelPerformResponse(
    val status: String?,
    val data: CancelPerformData?
)
data class CancelPerformData(
    val message: String?,
    val reservation_id: Int?,
    val refunded_amount: Double?
)
