package com.example.ticket_booking_manager_client.data.remote

import android.content.Context
import com.example.ticket_booking_manager_client.data.TokenStore
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object ApiClient {
    private const val BASE_URL = "http://31.56.227.174:5000/"

    fun create(context: Context): ApiService {
        val tokenStore = TokenStore(context)

        val authInterceptor = Interceptor { chain ->
            val original = chain.request()
            val url = original.url.toString()
            val builder = original.newBuilder()

            val isPublic = url.endsWith("/api/cities") || url.endsWith("/api/cities/")
            // Debug log
            android.util.Log.d("APP/HTTP", "Request: ${original.method} $url (public=$isPublic)")

            if (!isPublic) {
                val token = runBlocking { tokenStore.getTokenOnce() }
                android.util.Log.d("APP/HTTP", "Token present? ${!token.isNullOrBlank()}")
                if (!token.isNullOrBlank()) {
                    val headerValue = if (token.startsWith("Bearer ")) token else "Bearer $token"
                    builder.header("Authorization", headerValue)
                }
            } else {
                android.util.Log.d("APP/HTTP", "Skipping Authorization for public endpoint")
            }

            val req = builder.build()
            android.util.Log.d("APP/HTTP", "Proceed: ${req.method} ${req.url}")
            chain.proceed(req)
        }

        val logging = HttpLoggingInterceptor { msg ->
            // Prefix OkHttp logs for easy filtering
            android.util.Log.d("APP/OkHttp", msg)
        }.apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(logging)
            .addInterceptor(authInterceptor)
            .build()

        android.util.Log.d("APP/HTTP", "Retrofit BASE_URL=$BASE_URL")

        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}