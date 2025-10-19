package com.example.ticket_booking_manager_client.data.remote

import android.content.Context
import android.util.Log
import com.example.ticket_booking_manager_client.data.TokenStore
import com.example.ticket_booking_manager_client.net.RetryOnProtocolErrorInterceptor
import com.example.ticket_booking_manager_client.net.SafeBodyLoggingInterceptor
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object ApiClient {
    private const val BASE_URL = "http://10.0.2.2:5000/"

    fun create(context: Context): ApiService {
        val tokenStore = TokenStore(context)

        val authInterceptor = Interceptor { chain ->
            val original = chain.request()
            val url = original.url.toString()
            val path = original.url.encodedPath
            val builder = original.newBuilder()

            val isPublic = path == "/api/cities" || path == "/api/cities/"
            Log.d("APP/HTTP", "Request: ${original.method} $url (public=$isPublic)")

            if (!isPublic) {
                val token = runBlocking { tokenStore.getTokenOnce() }
                Log.d("APP/HTTP", "Token present? ${!token.isNullOrBlank()}")
                if (!token.isNullOrBlank()) {
                    val headerValue = if (token.startsWith("Bearer ")) token else "Bearer $token"
                    builder.header("Authorization", headerValue)
                }
            } else {
                Log.d("APP/HTTP", "Skipping Authorization for public endpoint")
            }

            // Tag fragile endpoints to skip body peek
            val method = original.method.uppercase()
            val skipPeek = method == "GET" && (
                    path == "/api/cities" || path == "/api/cities/" ||
                            path == "/api/tickets/search"
                    )
            if (skipPeek) {
                builder.header("X-No-Peek", "1")
            }

            val req = builder.build()
            Log.d("APP/HTTP", "Proceed: ${req.method} ${req.url}")
            chain.proceed(req)
        }

        val baseLogging = HttpLoggingInterceptor { msg ->
            Log.d("APP/OkHttp", msg)
        }.apply {
            level = HttpLoggingInterceptor.Level.HEADERS
        }

        val retryOnProto = RetryOnProtocolErrorInterceptor()
        val safeBodyLogging = SafeBodyLoggingInterceptor()

        val client = OkHttpClient.Builder()
            .connectTimeout(25, TimeUnit.SECONDS)
            .readTimeout(25, TimeUnit.SECONDS)
            .writeTimeout(25, TimeUnit.SECONDS)
            // Order matters: base headers log, auth tagging, retry, then body logging
            .addInterceptor(baseLogging)
            .addInterceptor(authInterceptor)
            .addInterceptor(retryOnProto)
            .addInterceptor(safeBodyLogging)
            .build()

        Log.d("APP/HTTP", "Retrofit BASE_URL=$BASE_URL")

        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}